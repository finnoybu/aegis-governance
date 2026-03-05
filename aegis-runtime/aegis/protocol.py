"""AGP – AEGIS Governance Protocol.

Defines the wire-level request and response structures used by all
AEGIS components.  Every interaction between an AI agent and governed
infrastructure passes through these dataclasses.

Protocol flow
-------------
1. Agent constructs an :class:`AGPRequest` describing the proposed action.
2. The :class:`GovernanceGateway` receives the request.
3. The :class:`DecisionEngine` evaluates it and emits an :class:`AGPResponse`.
4. Only ``Decision.APPROVED`` responses allow the action to proceed.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Decision(str, Enum):
    """Possible outcomes of a governance decision."""

    APPROVED = "approved"
    """The action is permitted and may proceed."""

    DENIED = "denied"
    """The action is prohibited and must not proceed."""

    DEFERRED = "deferred"
    """A definitive decision requires human or higher-authority review."""


class ActionType(str, Enum):
    """Canonical categories of actions an AI agent may propose."""

    TOOL_CALL = "tool_call"
    """Invocation of a registered tool."""

    FILE_READ = "file_read"
    """Reading from the file-system."""

    FILE_WRITE = "file_write"
    """Writing or modifying the file-system."""

    API_CALL = "api_call"
    """An outbound HTTP/RPC call to an external service."""

    SHELL_EXEC = "shell_exec"
    """Execution of an arbitrary shell command."""

    DATA_ACCESS = "data_access"
    """Reading from or writing to a data store."""


@dataclass
class AGPAction:
    """Describes the specific action an agent is proposing."""

    type: ActionType
    """Category of the action (see :class:`ActionType`)."""

    target: str
    """The resource identifier the action targets (URI, path, tool name, …)."""

    parameters: dict[str, Any] = field(default_factory=dict)
    """Arbitrary key/value parameters required by the action."""


@dataclass
class AGPContext:
    """Execution context accompanying an AGP request."""

    session_id: str
    """Opaque identifier for the agent's current session."""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """UTC timestamp when the context was created."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Supplementary metadata (e.g. environment, user-id, trace-id)."""


@dataclass
class AGPRequest:
    """A governance request submitted by an AI agent via AGP."""

    agent_id: str
    """Stable identifier for the requesting AI agent."""

    action: AGPAction
    """The proposed action subject to governance evaluation."""

    context: AGPContext
    """Session and environmental context."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique request identifier (auto-generated UUID4 by default)."""


@dataclass
class AGPResponse:
    """A governance decision returned by the AEGIS Decision Engine."""

    request_id: str
    """Echoes the :attr:`AGPRequest.request_id` this response corresponds to."""

    decision: Decision
    """The governance decision."""

    reason: str
    """Human-readable explanation of the decision."""

    audit_id: str
    """Identifier of the immutable audit record created for this decision."""

    conditions: list[str] = field(default_factory=list)
    """Optional conditions that must be observed if the action is approved."""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """UTC timestamp of the decision."""
