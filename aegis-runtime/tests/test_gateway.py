"""Tests for the GovernanceGateway."""

import pytest
from unittest.mock import Mock

from aegis import AEGISRuntime
from aegis.capability_registry import Capability
from aegis.exceptions import AEGISValidationError
from aegis.gateway import GovernanceGateway
from aegis.policy_engine import Policy, PolicyEffect
from aegis.protocol import (
    AGPAction,
    AGPContext,
    AGPRequest,
    AGPResponse,
    ActionType,
    Decision,
)


@pytest.fixture()
def runtime() -> AEGISRuntime:
    rt = AEGISRuntime()
    cap = Capability(
        id="cap-1",
        name="All",
        description="",
        action_types=["tool_call"],
        target_patterns=["*"],
    )
    rt.capabilities.register(cap)
    rt.capabilities.grant("agent-1", "cap-1")
    rt.policies.add_policy(Policy(
        id="pol-allow",
        name="Allow all",
        description="",
        effect=PolicyEffect.ALLOW,
        conditions=[],
    ))
    return rt


def make_request(**overrides) -> AGPRequest:
    defaults = dict(
        agent_id="agent-1",
        action=AGPAction(type=ActionType.TOOL_CALL, target="my_tool"),
        context=AGPContext(session_id="sess-1"),
    )
    defaults.update(overrides)
    return AGPRequest(**defaults)


class TestValidation:
    """Test request validation at the gateway."""

    # ============================================================
    # Agent ID Validation
    # ============================================================

    def test_empty_agent_id_raises(self, runtime):
        req = make_request(agent_id="")
        with pytest.raises(AEGISValidationError, match="agent_id.*empty"):
            runtime.gateway.submit(req)

    def test_none_request_raises(self, runtime):
        with pytest.raises(AEGISValidationError, match="must not be None"):
            runtime.gateway.submit(None)

    def test_blank_agent_id_raises(self, runtime):
        req = make_request(agent_id="   ")
        with pytest.raises(AEGISValidationError, match="agent_id.*empty"):
            runtime.gateway.submit(req)

    def test_none_agent_id_raises(self, runtime):
        req = make_request(agent_id=None)
        with pytest.raises(AEGISValidationError, match="agent_id.*empty"):
            runtime.gateway.submit(req)

    def test_agent_id_with_invalid_chars_raises(self, runtime):
        invalid_ids = [
            "agent@1",      # @ not allowed
            "agent 1",      # space not allowed
            "agent!1",      # ! not allowed
            "agent$1",      # $ not allowed
            "agent/1",      # / not allowed
        ]
        for invalid_id in invalid_ids:
            req = make_request(agent_id=invalid_id)
            with pytest.raises(AEGISValidationError, match="invalid characters"):
                runtime.gateway.submit(req)

    def test_agent_id_with_valid_special_chars_passes(self, runtime):
        valid_ids = [
            "agent-1",      # hyphen allowed
            "agent_1",      # underscore allowed
            "agent.1",      # dot allowed
            "agent-1_2.3",  # all allowed mixed
        ]
        for valid_id in valid_ids:
            req = make_request(agent_id=valid_id)
            response = runtime.gateway.submit(req)
            assert response.request_id is not None

    def test_agent_id_exceeds_max_length_raises(self, runtime):
        agent_id = "a" * 257
        req = make_request(agent_id=agent_id)
        with pytest.raises(AEGISValidationError, match="exceeds maximum length"):
            runtime.gateway.submit(req)

    # ============================================================
    # Action Validation
    # ============================================================

    def test_none_action_raises(self, runtime):
        req = make_request(action=None)
        with pytest.raises(AEGISValidationError, match="action.*None"):
            runtime.gateway.submit(req)

    def test_empty_action_type_raises(self, runtime):
        action = AGPAction(type=None, target="my_tool")
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="action.type"):
            runtime.gateway.submit(req)

    def test_invalid_action_type_value_raises(self, runtime):
        # Non-enum action type should be rejected by gateway validation.
        action = AGPAction(type="tool_call", target="my_tool")
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="valid ActionType"):
            runtime.gateway.submit(req)

    def test_invalid_action_type_numeric_raises(self, runtime):
        # Numeric value is malformed and must fail semantic validation.
        action = AGPAction(type=123, target="my_tool")
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="valid ActionType"):
            runtime.gateway.submit(req)

    def test_empty_target_raises(self, runtime):
        req = make_request(action=AGPAction(type=ActionType.TOOL_CALL, target=""))
        with pytest.raises(AEGISValidationError, match="target.*empty"):
            runtime.gateway.submit(req)

    def test_blank_target_raises(self, runtime):
        req = make_request(action=AGPAction(type=ActionType.TOOL_CALL, target="   "))
        with pytest.raises(AEGISValidationError, match="target.*empty"):
            runtime.gateway.submit(req)

    def test_target_exceeds_max_length_raises(self, runtime):
        target = "t" * 1025
        action = AGPAction(type=ActionType.TOOL_CALL, target=target)
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="exceeds maximum length"):
            runtime.gateway.submit(req)

    def test_none_parameters_raises(self, runtime):
        action = AGPAction(
            type=ActionType.TOOL_CALL,
            target="my_tool",
            parameters=None
        )
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="parameters.*None"):
            runtime.gateway.submit(req)

    def test_invalid_parameters_type_raises(self, runtime):
        action = AGPAction(
            type=ActionType.TOOL_CALL,
            target="my_tool",
            parameters="not-a-dict"  # Should be dict
        )
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="parameters.*dict"):
            runtime.gateway.submit(req)

    def test_none_parameter_key_raises(self, runtime):
        action = AGPAction(
            type=ActionType.TOOL_CALL,
            target="my_tool",
            parameters={None: "value"}  # None key invalid
        )
        req = make_request(action=action)
        with pytest.raises(AEGISValidationError, match="None key"):
            runtime.gateway.submit(req)

    # ============================================================
    # Context Validation
    # ============================================================

    def test_none_context_raises(self, runtime):
        req = make_request(context=None)
        with pytest.raises(AEGISValidationError, match="context.*None"):
            runtime.gateway.submit(req)

    def test_empty_session_id_raises(self, runtime):
        req = make_request(context=AGPContext(session_id=""))
        with pytest.raises(AEGISValidationError, match="session_id.*empty"):
            runtime.gateway.submit(req)

    def test_blank_session_id_raises(self, runtime):
        req = make_request(context=AGPContext(session_id="   "))
        with pytest.raises(AEGISValidationError, match="session_id.*empty"):
            runtime.gateway.submit(req)

    def test_session_id_exceeds_max_length_raises(self, runtime):
        session_id = "s" * 257
        req = make_request(context=AGPContext(session_id=session_id))
        with pytest.raises(AEGISValidationError, match="exceeds maximum length"):
            runtime.gateway.submit(req)

    def test_none_timestamp_raises(self, runtime):
        ctx = AGPContext(session_id="sess-1", timestamp=None)
        req = make_request(context=ctx)
        with pytest.raises(AEGISValidationError, match="timestamp"):
            runtime.gateway.submit(req)

    def test_none_metadata_raises(self, runtime):
        ctx = AGPContext(session_id="sess-1")
        ctx.metadata = None
        req = make_request(context=ctx)
        with pytest.raises(AEGISValidationError, match="metadata"):
            runtime.gateway.submit(req)

    # ============================================================
    # Request ID Validation
    # ============================================================

    def test_none_request_id_raises(self, runtime):
        req = make_request()
        req.request_id = None
        with pytest.raises(AEGISValidationError, match="request_id"):
            runtime.gateway.submit(req)

    def test_empty_request_id_raises(self, runtime):
        req = make_request()
        req.request_id = ""
        with pytest.raises(AEGISValidationError, match="request_id"):
            runtime.gateway.submit(req)


class TestSubmit:
    def test_valid_request_returns_response(self, runtime):
        response = runtime.gateway.submit(make_request())
        assert response.decision == Decision.APPROVED

    def test_request_id_echoed(self, runtime):
        req = make_request()
        response = runtime.gateway.submit(req)
        assert response.request_id == req.request_id

    def test_denied_request_returns_response(self, runtime):
        # Agent with no capability
        req = make_request(agent_id="unknown-agent")
        response = runtime.gateway.submit(req)
        assert response.decision == Decision.DENIED


class TestRouting:
    def test_valid_request_is_routed_to_decision_engine(self):
        request = make_request()
        expected = AGPResponse(
            request_id=request.request_id,
            decision=Decision.APPROVED,
            reason="ok",
            audit_id="audit-1",
        )
        engine = Mock()
        engine.evaluate.return_value = expected
        gateway = GovernanceGateway(engine)

        response = gateway.submit(request)

        engine.evaluate.assert_called_once_with(request)
        assert response == expected

    def test_invalid_request_is_not_routed(self):
        request = make_request(agent_id="")
        engine = Mock()
        gateway = GovernanceGateway(engine)

        with pytest.raises(AEGISValidationError):
            gateway.submit(request)

        engine.evaluate.assert_not_called()
