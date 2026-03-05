"""AEGISRuntime – convenience facade.

Wires all AEGIS components together into a single object that can be
used as the primary integration point for embedders.

Quick-start::

    from aegis import AEGISRuntime
    from aegis.capability_registry import Capability
    from aegis.policy_engine import Policy, PolicyEffect, PolicyCondition
    from aegis.protocol import ActionType

    runtime = AEGISRuntime()

    # 1. Register a capability
    runtime.capabilities.register(Capability(
        id="cap-read-docs",
        name="Read documentation files",
        description="Allows reading files under /docs",
        action_types=[ActionType.FILE_READ.value, ActionType.TOOL_CALL.value],
        target_patterns=["/docs/*", "read_*"],
    ))

    # 2. Grant the capability to an agent
    runtime.capabilities.grant("agent-1", "cap-read-docs")

    # 3. Add an allow policy
    runtime.policies.add_policy(Policy(
        id="pol-allow-docs",
        name="Allow documentation reads",
        description="Agents with the docs capability may read documentation.",
        effect=PolicyEffect.ALLOW,
        conditions=[],  # no extra conditions – capability check is sufficient
    ))

    # 4. Create a governed tool proxy for the agent
    proxy = runtime.create_tool_proxy("agent-1", "session-xyz")
    proxy.register_tool("read_doc", fn=lambda path: open(path).read(), target="read_doc")

    # 5. Invoke the tool – governance is applied transparently
    content = proxy.call("read_doc", path="/docs/intro.md")
"""

from __future__ import annotations

from .audit import AuditSystem
from .capability_registry import CapabilityRegistry
from .decision_engine import DecisionEngine
from .gateway import GovernanceGateway
from .policy_engine import PolicyEngine
from .tool_proxy import ToolProxy


class AEGISRuntime:
    """A fully assembled AEGIS governance runtime.

    Each component is publicly accessible so that callers can configure
    capabilities and policies directly, while the plumbing (audit,
    decision engine, gateway) is set up automatically.

    Parameters
    ----------
    db_path:
        SQLite database path for the :class:`~aegis.audit.AuditSystem`.
        Defaults to ``":memory:"`` (in-process, no persistence).
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._audit = AuditSystem(db_path=db_path)
        self._capabilities = CapabilityRegistry()
        self._policies = PolicyEngine()
        self._decision_engine = DecisionEngine(
            capability_registry=self._capabilities,
            policy_engine=self._policies,
            audit_system=self._audit,
        )
        self._gateway = GovernanceGateway(decision_engine=self._decision_engine)

    # ------------------------------------------------------------------
    # Public component accessors
    # ------------------------------------------------------------------

    @property
    def capabilities(self) -> CapabilityRegistry:
        """The :class:`~aegis.capability_registry.CapabilityRegistry`."""
        return self._capabilities

    @property
    def policies(self) -> PolicyEngine:
        """The :class:`~aegis.policy_engine.PolicyEngine`."""
        return self._policies

    @property
    def audit(self) -> AuditSystem:
        """The :class:`~aegis.audit.AuditSystem`."""
        return self._audit

    @property
    def gateway(self) -> GovernanceGateway:
        """The :class:`~aegis.gateway.GovernanceGateway`."""
        return self._gateway

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def create_tool_proxy(self, agent_id: str, session_id: str) -> ToolProxy:
        """Create a :class:`~aegis.tool_proxy.ToolProxy` bound to this runtime.

        Parameters
        ----------
        agent_id:
            The AI agent that will use the proxy.
        session_id:
            The current session identifier.
        """
        return ToolProxy(
            gateway=self._gateway,
            agent_id=agent_id,
            session_id=session_id,
        )
