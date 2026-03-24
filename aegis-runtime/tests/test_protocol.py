"""Tests for the AGP (AEGIS Governance Protocol) data structures."""

import uuid
from datetime import datetime, timezone

import pytest

from aegis.protocol import (
    AGPAction,
    AGPContext,
    AGPRequest,
    AGPResponse,
    ActionType,
    Decision,
)


class TestDecision:
    def test_values(self):
        assert Decision.APPROVED == "approved"
        assert Decision.DENIED == "denied"
        assert Decision.ESCALATE == "escalate"
        assert Decision.REQUIRE_CONFIRMATION == "require_confirmation"

    def test_string_comparison(self):
        assert Decision.APPROVED == "approved"


class TestActionType:
    def test_all_types_present(self):
        types = {at.value for at in ActionType}
        assert "tool_call" in types
        assert "file_read" in types
        assert "file_write" in types
        assert "api_call" in types
        assert "shell_exec" in types
        assert "data_access" in types


class TestAGPAction:
    """Test AGPAction dataclass."""

    def test_defaults(self):
        action = AGPAction(type=ActionType.TOOL_CALL, target="my_tool")
        assert action.parameters == {}

    def test_custom_parameters(self):
        action = AGPAction(
            type=ActionType.FILE_READ,
            target="/etc/hosts",
            parameters={"encoding": "utf-8"},
        )
        assert action.parameters["encoding"] == "utf-8"

    # ========================================================
    # Serialization Tests
    # ========================================================

    def test_to_dict(self):
        action = AGPAction(
            type=ActionType.FILE_READ,
            target="/etc/hosts",
            parameters={"encoding": "utf-8"},
        )
        d = action.to_dict()
        assert d["type"] == "file_read"
        assert d["target"] == "/etc/hosts"
        assert d["parameters"]["encoding"] == "utf-8"

    def test_to_json_and_from_json(self):
        action = AGPAction(
            type=ActionType.TOOL_CALL,
            target="my_tool",
            parameters={"arg1": "value1"},
        )
        json_str = action.to_json()
        parsed = AGPAction.from_json(json_str)
        assert parsed.type == action.type
        assert parsed.target == action.target
        assert parsed.parameters == action.parameters

    def test_from_json_roundtrip_preserves_data(self):
        original = AGPAction(
            type=ActionType.API_CALL,
            target="https://example.com/api",
            parameters={"method": "POST", "headers": {"X-Custom": "value"}},
        )
        json_str = original.to_json()
        restored = AGPAction.from_json(json_str)
        assert restored == original


class TestAGPContext:
    """Test AGPContext dataclass."""

    def test_auto_timestamp(self):
        ctx = AGPContext(session_id="sess-1")
        assert isinstance(ctx.timestamp, datetime)
        assert ctx.timestamp.tzinfo is not None

    def test_metadata_defaults(self):
        ctx = AGPContext(session_id="sess-1")
        assert ctx.metadata == {}

    # ========================================================
    # Serialization Tests
    # ========================================================

    def test_to_dict(self):
        ctx = AGPContext(
            session_id="sess-1",
            metadata={"user_id": "user-123"},
        )
        d = ctx.to_dict()
        assert d["session_id"] == "sess-1"
        assert d["metadata"]["user_id"] == "user-123"
        assert "timestamp" in d

    def test_to_json_and_from_json(self):
        original = AGPContext(
            session_id="sess-1",
            metadata={"env": "prod"},
        )
        json_str = original.to_json()
        parsed = AGPContext.from_json(json_str)
        assert parsed.session_id == original.session_id
        assert parsed.metadata == original.metadata

    def test_from_json_roundtrip_preserves_timestamp(self):
        original = AGPContext(session_id="sess-1")
        json_str = original.to_json()
        restored = AGPContext.from_json(json_str)
        # Timestamps should be equal (ISO format roundtrip)
        assert restored.timestamp == original.timestamp


class TestAGPRequest:
    """Test AGPRequest dataclass."""

    def test_auto_request_id(self):
        req = AGPRequest(
            agent_id="agent-1",
            action=AGPAction(type=ActionType.TOOL_CALL, target="tool"),
            context=AGPContext(session_id="sess-1"),
        )
        # Should be a valid UUID
        uuid.UUID(req.request_id)

    def test_unique_request_ids(self):
        make_req = lambda: AGPRequest(
            agent_id="a",
            action=AGPAction(type=ActionType.TOOL_CALL, target="t"),
            context=AGPContext(session_id="s"),
        )
        assert make_req().request_id != make_req().request_id

    def test_explicit_request_id(self):
        req = AGPRequest(
            agent_id="a",
            action=AGPAction(type=ActionType.TOOL_CALL, target="t"),
            context=AGPContext(session_id="s"),
            request_id="custom-id",
        )
        assert req.request_id == "custom-id"

    # ========================================================
    # Serialization Tests
    # ========================================================

    def test_to_dict(self):
        req = AGPRequest(
            agent_id="agent-1",
            action=AGPAction(type=ActionType.FILE_READ, target="/etc/hosts"),
            context=AGPContext(session_id="sess-1"),
            request_id="req-123",
        )
        d = req.to_dict()
        assert d["agent_id"] == "agent-1"
        assert d["request_id"] == "req-123"
        assert d["action"]["type"] == "file_read"
        assert d["context"]["session_id"] == "sess-1"

    def test_to_json_and_from_json(self):
        original = AGPRequest(
            agent_id="agent-1",
            action=AGPAction(
                type=ActionType.TOOL_CALL,
                target="my_tool",
                parameters={"key": "value"},
            ),
            context=AGPContext(session_id="sess-1", metadata={"trace_id": "t1"}),
            request_id="req-123",
        )
        json_str = original.to_json()
        parsed = AGPRequest.from_json(json_str)
        assert parsed.agent_id == original.agent_id
        assert parsed.request_id == original.request_id
        assert parsed.action.type == original.action.type
        assert parsed.context.session_id == original.context.session_id

    def test_from_json_roundtrip_preserves_all_data(self):
        original = AGPRequest(
            agent_id="bot-1",
            action=AGPAction(
                type=ActionType.API_CALL,
                target="https://example.com/api",
                parameters={"method": "GET", "headers": {"Auth": "token"}},
            ),
            context=AGPContext(
                session_id="session-abc",
                metadata={"user_id": "user-123", "env": "prod"},
            ),
            request_id="req-custom-123",
        )
        json_str = original.to_json()
        restored = AGPRequest.from_json(json_str)

        # Verify all fields match
        assert restored.agent_id == original.agent_id
        assert restored.request_id == original.request_id
        assert restored.action.type == original.action.type
        assert restored.action.target == original.action.target
        assert restored.action.parameters == original.action.parameters
        assert restored.context.session_id == original.context.session_id
        assert restored.context.metadata == original.context.metadata


class TestAGPResponse:
    """Test AGPResponse dataclass."""

    def test_required_fields(self):
        resp = AGPResponse(
            request_id="req-1",
            decision=Decision.APPROVED,
            reason="Approved by policy.",
            audit_id="aud-1",
        )
        assert resp.decision == Decision.APPROVED

    # ========================================================
    # Serialization Tests
    # ========================================================

    def test_to_dict(self):
        resp = AGPResponse(
            request_id="req-1",
            decision=Decision.APPROVED,
            reason="Approved by policy.",
            audit_id="aud-123",
            conditions=["condition-1"],
        )
        d = resp.to_dict()
        assert d["request_id"] == "req-1"
        assert d["decision"] == "approved"
        assert d["reason"] == "Approved by policy."
        assert d["audit_id"] == "aud-123"
        assert d["conditions"] == ["condition-1"]
        assert "timestamp" in d

    def test_to_json_and_from_json(self):
        original = AGPResponse(
            request_id="req-1",
            decision=Decision.DENIED,
            reason="Not authorized.",
            audit_id="aud-1",
            conditions=["condition-1", "condition-2"],
        )
        json_str = original.to_json()
        parsed = AGPResponse.from_json(json_str)
        assert parsed.request_id == original.request_id
        assert parsed.decision == original.decision
        assert parsed.reason == original.reason
        assert parsed.audit_id == original.audit_id
        assert parsed.conditions == original.conditions

    def test_from_json_roundtrip_all_decisions(self):
        for decision in [Decision.APPROVED, Decision.DENIED, Decision.ESCALATE, Decision.REQUIRE_CONFIRMATION]:
            original = AGPResponse(
                request_id="req-123",
                decision=decision,
                reason=f"Response with {decision}",
                audit_id="aud-456",
            )
            json_str = original.to_json()
            restored = AGPResponse.from_json(json_str)
            assert restored.decision == decision
            assert restored.decision.value == decision.value
            assert restored.conditions == []
            assert isinstance(restored.timestamp, datetime)
