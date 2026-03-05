"""Capability Registry.

Implements the capability-based access model that forms the first layer
of AEGIS's defence-in-depth strategy.

An agent is only permitted to attempt an action if it holds a capability
that covers both the :class:`~aegis.protocol.ActionType` and the target
resource.  Capabilities can be time-limited and are revocable at any
time.

Design
------
* Capabilities are registered globally (shared across all agents).
* Each agent is granted zero or more capability IDs.
* A capability covers one or more action types and a set of target
  patterns (``fnmatch`` glob syntax, e.g. ``"s3://my-bucket/*"``).
* A capability whose ``expires_at`` is in the past is treated as
  non-existent.
* All operations are thread-safe via internal locking.
"""

from __future__ import annotations

import fnmatch
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .exceptions import AEGISCapabilityError


@dataclass
class Capability:
    """A named, scoped permission unit.

    Parameters
    ----------
    id : str
        Unique identifier for this capability.
    name : str
        Short human-readable label.
    description : str
        Longer description of what this capability allows.
    action_types : list[str]
        List of :class:`~aegis.protocol.ActionType` values (as strings)
        covered by this capability.
    target_patterns : list[str]
        List of ``fnmatch`` glob patterns matching permissible targets.
        Use ``["*"]`` to match any target.
    granted_at : datetime, optional
        UTC timestamp when the capability was created.
    expires_at : datetime, optional
        Optional UTC expiry timestamp.  ``None`` means never expires.
    metadata : dict, optional
        Arbitrary key/value annotations.
    """

    id: str
    name: str
    description: str
    action_types: list[str]
    target_patterns: list[str]
    granted_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def is_active(self, at: datetime | None = None) -> bool:
        """Return ``True`` if the capability has not expired.
        
        Parameters
        ----------
        at : datetime, optional
            Reference time. Defaults to now(UTC).
            
        Returns
        -------
        bool
            True if the capability is currently active.
        """
        if self.expires_at is None:
            return True
        reference = at or datetime.now(timezone.utc)
        return self.expires_at > reference

    def covers(self, action_type: str, target: str) -> bool:
        """Return ``True`` if this capability permits *action_type* on *target*.
        
        Parameters
        ----------
        action_type : str
            The action type to check (e.g., "tool_call", "file_read").
        target : str
            The resource target to check (e.g., "/docs/*").
            
        Returns
        -------
        bool
            True if this capability covers the action+target combination.
        """
        if not self.is_active():
            return False
        if action_type not in self.action_types:
            return False
        return any(
            fnmatch.fnmatch(target, pattern) or pattern == "*"
            for pattern in self.target_patterns
        )


class CapabilityRegistry:
    """Central store of capabilities and their assignments to agents.

    This implementation is thread-safe via internal locking. All database
    operations are protected to enable safe concurrent access from multiple
    threads.
    """

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        self._agent_capabilities: dict[str, set[str]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Capability management
    # ------------------------------------------------------------------

    def register(self, capability: Capability) -> None:
        """Register a new capability definition.

        Parameters
        ----------
        capability : Capability
            The capability to register.
            
        Raises
        ------
        ValueError
            If a capability with the same ID is already registered.
        """
        with self._lock:
            if capability.id in self._capabilities:
                raise ValueError(f"Capability '{capability.id}' is already registered.")
            self._capabilities[capability.id] = capability

    def unregister(self, capability_id: str) -> None:
        """Remove a capability definition and all agent assignments for it.
        
        Parameters
        ----------
        capability_id : str
            ID of the capability to unregister.
        """
        with self._lock:
            self._capabilities.pop(capability_id, None)
            for agent_caps in self._agent_capabilities.values():
                agent_caps.discard(capability_id)

    def get_capability(self, capability_id: str) -> Capability | None:
        """Look up a capability by ID.
        
        Parameters
        ----------
        capability_id : str
            ID of the capability to retrieve.
            
        Returns
        -------
        Capability or None
            The capability if found, None otherwise.
        """
        with self._lock:
            return self._capabilities.get(capability_id)

    # ------------------------------------------------------------------
    # Agent assignments
    # ------------------------------------------------------------------

    def grant(self, agent_id: str, capability_id: str) -> None:
        """Grant *capability_id* to *agent_id*.

        Parameters
        ----------
        agent_id : str
            The agent to grant the capability to.
        capability_id : str
            The capability to grant.
            
        Raises
        ------
        AEGISCapabilityError
            If *capability_id* is not registered.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise AEGISCapabilityError(
                    f"Cannot grant unknown capability '{capability_id}'.",
                    error_code="UNKNOWN_CAPABILITY"
                )
            self._agent_capabilities.setdefault(agent_id, set()).add(capability_id)

    def bulk_grant(
        self,
        agent_ids: list[str],
        capability_id: str,
    ) -> int:
        """Grant a single capability to multiple agents.
        
        This is more efficient than calling grant() multiple times, as it
        performs all assignments in a single atomic transaction.

        Parameters
        ----------
        agent_ids : list[str]
            List of agent IDs to grant the capability to.
        capability_id : str
            The capability to grant to all agents.
            
        Returns
        -------
        int
            The number of agents that were granted the capability.
            
        Raises
        ------
        AEGISCapabilityError
            If *capability_id* is not registered.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise AEGISCapabilityError(
                    f"Cannot grant unknown capability '{capability_id}'.",
                    error_code="UNKNOWN_CAPABILITY"
                )
            count = 0
            for agent_id in agent_ids:
                if agent_id not in self._agent_capabilities:
                    self._agent_capabilities[agent_id] = set()
                if capability_id not in self._agent_capabilities[agent_id]:
                    self._agent_capabilities[agent_id].add(capability_id)
                    count += 1
            return count

    def revoke(self, agent_id: str, capability_id: str) -> None:
        """Revoke *capability_id* from *agent_id* (no-op if not held).
        
        Parameters
        ----------
        agent_id : str
            The agent to revoke the capability from.
        capability_id : str
            The capability to revoke.
        """
        with self._lock:
            if agent_id in self._agent_capabilities:
                self._agent_capabilities[agent_id].discard(capability_id)

    def bulk_revoke(
        self,
        agent_ids: list[str],
        capability_id: str,
    ) -> int:
        """Revoke a single capability from multiple agents.
        
        This is more efficient than calling revoke() multiple times, as it
        performs all revocations in a single atomic transaction.

        Parameters
        ----------
        agent_ids : list[str]
            List of agent IDs to revoke the capability from.
        capability_id : str
            The capability to revoke from all agents.
            
        Returns
        -------
        int
            The number of agents that had the capability revoked.
        """
        with self._lock:
            count = 0
            for agent_id in agent_ids:
                if agent_id in self._agent_capabilities:
                    if capability_id in self._agent_capabilities[agent_id]:
                        self._agent_capabilities[agent_id].discard(capability_id)
                        count += 1
            return count

    def revoke_all(self, agent_id: str) -> None:
        """Revoke all capabilities from *agent_id*.
        
        Parameters
        ----------
        agent_id : str
            The agent to revoke all capabilities from.
        """
        with self._lock:
            self._agent_capabilities.pop(agent_id, None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_agent_capabilities(self, agent_id: str) -> list[Capability]:
        """Return the active capabilities currently held by *agent_id*.
        
        Parameters
        ----------
        agent_id : str
            The agent to query.
            
        Returns
        -------
        list[Capability]
            List of active capabilities held by the agent.
        """
        with self._lock:
            cap_ids = self._agent_capabilities.get(agent_id, set())
            now = datetime.now(timezone.utc)
            return [
                self._capabilities[cid]
                for cid in cap_ids
                if cid in self._capabilities and self._capabilities[cid].is_active(now)
            ]

    def has_capability_for_action(
        self, agent_id: str, action_type: str, target: str
    ) -> bool:
        """Return ``True`` if *agent_id* holds a capability covering *action_type*
        on *target*.
        
        Parameters
        ----------
        agent_id : str
            The agent to check.
        action_type : str
            The action type (e.g., "tool_call").
        target : str
            The target resource.
            
        Returns
        -------
        bool
            True if the agent has a matching active capability.
        """
        return any(
            cap.covers(action_type, target)
            for cap in self.get_agent_capabilities(agent_id)
        )
