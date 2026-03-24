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
   ``ESCALATE`` and ``REQUIRE_CONFIRMATION`` halt execution pending review.

Serialization
-------------
All AGP dataclasses can be serialized to/from JSON using :meth:`to_json`
and :meth:`from_json`, enabling use over REST APIs, message queues, or
other JSON-based transports.

Example:
    >>> request = AGPRequest(agent_id="bot", action=...)
    >>> json_str = request.to_json()
    >>> parsed = AGPRequest.from_json(json_str)
"""

from __future__ import annotations

import json
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

    ESCALATE = "escalate"
    """The action requires elevated review before proceeding."""

    REQUIRE_CONFIRMATION = "require_confirmation"
    """The action requires explicit human approval before proceeding."""


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
    """Describes the specific action an agent is proposing.
    
    Parameters
    ----------
    type : ActionType
        Category of the action (see :class:`ActionType`).
    target : str
        The resource identifier the action targets (URI, path, tool name, …).
    parameters : dict, optional
        Arbitrary key/value parameters required by the action.
    """

    type: ActionType
    """Category of the action (see :class:`ActionType`)."""

    target: str
    """The resource identifier the action targets (URI, path, tool name, …)."""

    parameters: dict[str, Any] = field(default_factory=dict)
    """Arbitrary key/value parameters required by the action."""

    def to_dict(self) -> dict[str, Any]:
        """Convert this action to a dictionary.
        
        Returns
        -------
        dict
            Serializable dictionary representation.
        """
        return {
            "type": self.type.value,
            "target": self.target,
            "parameters": self.parameters,
        }

    def to_json(self) -> str:
        """Serialize this action to JSON.
        
        Returns
        -------
        str
            JSON-encoded action.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> AGPAction:
        """Deserialize an action from JSON.
        
        Parameters
        ----------
        json_str : str
            JSON string encoding an AGPAction.
            
        Returns
        -------
        AGPAction
            Deserialized action.
        """
        data = json.loads(json_str)
        return cls(
            type=ActionType(data["type"]),
            target=data["target"],
            parameters=data.get("parameters", {}),
        )


@dataclass
class AGPContext:
    """Execution context accompanying an AGP request.
    
    Parameters
    ----------
    session_id : str
        Opaque identifier for the agent's current session.
    timestamp : datetime, optional
        UTC timestamp when the context was created.
    metadata : dict, optional
        Supplementary metadata (e.g. environment, user-id, trace-id).
    """

    session_id: str
    """Opaque identifier for the agent's current session."""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """UTC timestamp when the context was created."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Supplementary metadata (e.g. environment, user-id, trace-id)."""

    def to_dict(self) -> dict[str, Any]:
        """Convert this context to a dictionary.
        
        Returns
        -------
        dict
            Serializable dictionary representation.
        """
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serialize this context to JSON.
        
        Returns
        -------
        str
            JSON-encoded context.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> AGPContext:
        """Deserialize a context from JSON.
        
        Parameters
        ----------
        json_str : str
            JSON string encoding an AGPContext.
            
        Returns
        -------
        AGPContext
            Deserialized context.
        """
        data = json.loads(json_str)
        return cls(
            session_id=data["session_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AGPRequest:
    """A governance request submitted by an AI agent via AGP.
    
    Parameters
    ----------
    agent_id : str
        Stable identifier for the requesting AI agent.
    action : AGPAction
        The proposed action subject to governance evaluation.
    context : AGPContext
        Session and environmental context.
    request_id : str, optional
        Unique request identifier (auto-generated UUID4 by default).
    """

    agent_id: str
    """Stable identifier for the requesting AI agent."""

    action: AGPAction
    """The proposed action subject to governance evaluation."""

    context: AGPContext
    """Session and environmental context."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique request identifier (auto-generated UUID4 by default)."""

    def to_dict(self) -> dict[str, Any]:
        """Convert this request to a dictionary.
        
        Returns
        -------
        dict
            Serializable dictionary representation.
        """
        return {
            "agent_id": self.agent_id,
            "action": self.action.to_dict(),
            "context": self.context.to_dict(),
            "request_id": self.request_id,
        }

    def to_json(self) -> str:
        """Serialize this request to JSON.
        
        Returns
        -------
        str
            JSON-encoded request.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> AGPRequest:
        """Deserialize a request from JSON.
        
        Parameters
        ----------
        json_str : str
            JSON string encoding an AGPRequest.
            
        Returns
        -------
        AGPRequest
            Deserialized request.
        """
        data = json.loads(json_str)
        return cls(
            agent_id=data["agent_id"],
            action=AGPAction.from_json(json.dumps(data["action"])),
            context=AGPContext.from_json(json.dumps(data["context"])),
            request_id=data["request_id"],
        )


@dataclass
class AGPResponse:
    """A governance decision returned by the AEGIS Decision Engine.
    
    Parameters
    ----------
    request_id : str
        Echoes the :attr:`AGPRequest.request_id` this response corresponds to.
    decision : Decision
        The governance decision.
    reason : str
        Human-readable explanation of the decision.
    audit_id : str
        Identifier of the immutable audit record created for this decision.
    conditions : list, optional
        Optional conditions that must be observed if the action is approved.
    timestamp : datetime, optional
        UTC timestamp of the decision.
    """

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

    def to_dict(self) -> dict[str, Any]:
        """Convert this response to a dictionary.
        
        Returns
        -------
        dict
            Serializable dictionary representation.
        """
        return {
            "request_id": self.request_id,
            "decision": self.decision.value,
            "reason": self.reason,
            "audit_id": self.audit_id,
            "conditions": self.conditions,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Serialize this response to JSON.
        
        Returns
        -------
        str
            JSON-encoded response.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> AGPResponse:
        """Deserialize a response from JSON.
        
        Parameters
        ----------
        json_str : str
            JSON string encoding an AGPResponse.
            
        Returns
        -------
        AGPResponse
            Deserialized response.
        """
        data = json.loads(json_str)
        return cls(
            request_id=data["request_id"],
            decision=Decision(data["decision"]),
            reason=data["reason"],
            audit_id=data["audit_id"],
            conditions=data.get("conditions", []),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
