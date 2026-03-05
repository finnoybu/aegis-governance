"""Tests for the DecisionEngine."""

import pytest

from aegis.audit import AuditSystem
from aegis.capability_registry import Capability, CapabilityRegistry
from aegis.decision_engine import DecisionEngine
from aegis.policy_engine import Policy, PolicyCondition, PolicyEffect, PolicyEngine
from aegis.protocol import AGPAction, AGPContext, AGPRequest, ActionType, Decision


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def audit():
    return AuditSystem()


@pytest.fixture()
def registry():
    return CapabilityRegistry()


@pytest.fixture()
def policies():
    return PolicyEngine()


@pytest.fixture()
def engine(registry, policies, audit):
    return DecisionEngine(
        capability_registry=registry,
        policy_engine=policies,
        audit_system=audit,
    )


def make_request(
    agent_id: str = "agent-1",
    action_type: ActionType = ActionType.TOOL_CALL,
    target: str = "my_tool",
) -> AGPRequest:
    return AGPRequest(
        agent_id=agent_id,
        action=AGPAction(type=action_type, target=target),
        context=AGPContext(session_id="sess-1"),
    )


def setup_allow(registry: CapabilityRegistry, policies: PolicyEngine,
                agent_id: str = "agent-1") -> None:
    """Grant capability and add a permissive allow policy."""
    cap = Capability(
        id="cap-1",
        name="All tools",
        description="",
        action_types=["tool_call"],
        target_patterns=["*"],
    )
    # Only register if not already there
    try:
        registry.register(cap)
    except ValueError:
        pass  # Already registered
    
    registry.grant(agent_id, "cap-1")
    
    # Only add policy if not already there
    if "pol-allow" not in [p.id for p in policies.list_policies()]:
        policies.add_policy(Policy(
            id="pol-allow",
            name="Allow all",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[],
        ))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCapabilityGate:
    def test_no_capability_denies(self, engine):
        response = engine.evaluate(make_request())
        assert response.decision == Decision.DENIED
        assert "lacks a capability" in response.reason

    def test_with_capability_proceeds_to_policy(self, engine, registry, policies):
        setup_allow(registry, policies)
        response = engine.evaluate(make_request())
        assert response.decision == Decision.APPROVED


class TestPolicyGate:
    def test_capability_present_but_no_policy_denies(self, engine, registry):
        cap = Capability(
            id="cap-1",
            name="Tools",
            description="",
            action_types=["tool_call"],
            target_patterns=["*"],
        )
        registry.register(cap)
        registry.grant("agent-1", "cap-1")
        # No allow policy added → default-deny
        response = engine.evaluate(make_request())
        assert response.decision == Decision.DENIED
        assert "default-deny" in response.reason

    def test_deny_policy_overrides_capability(self, engine, registry, policies):
        setup_allow(registry, policies)
        # Add a higher-priority deny policy
        policies.add_policy(Policy(
            id="pol-deny",
            name="Emergency deny",
            description="",
            effect=PolicyEffect.DENY,
            conditions=[],
            priority=0,
        ))
        response = engine.evaluate(make_request())
        assert response.decision == Decision.DENIED


class TestAuditIntegration:
    def test_approved_decision_is_audited(self, engine, registry, policies, audit):
        setup_allow(registry, policies)
        response = engine.evaluate(make_request())
        record = audit.get_record(response.audit_id)
        assert record is not None
        assert record.decision == "approved"
        assert record.agent_id == "agent-1"
        assert record.action_type == "tool_call"

    def test_denied_decision_is_also_audited(self, engine, audit):
        response = engine.evaluate(make_request())
        record = audit.get_record(response.audit_id)
        assert record is not None
        assert record.decision == "denied"

    def test_audit_id_in_response(self, engine, registry, policies, audit):
        setup_allow(registry, policies)
        response = engine.evaluate(make_request())
        assert response.audit_id
        assert audit.get_record(response.audit_id) is not None


class TestResponseFields:
    def test_request_id_echoed(self, engine, registry, policies):
        setup_allow(registry, policies)
        req = make_request()
        response = engine.evaluate(req)
        assert response.request_id == req.request_id

    def test_policy_evaluations_in_audit(self, engine, registry, policies, audit):
        setup_allow(registry, policies)
        response = engine.evaluate(make_request())
        record = audit.get_record(response.audit_id)
        assert isinstance(record.policy_evaluations, list)
        assert len(record.policy_evaluations) >= 1


class TestDecisionMetrics:
    """Test decision metrics collection and reporting."""

    def test_metrics_initial_state(self, engine):
        """Fresh engine has zero metrics."""
        metrics = engine.get_metrics()
        assert metrics.total_decisions == 0
        assert metrics.approved_count == 0
        assert metrics.denied_count == 0
        assert metrics.deferred_count == 0
        assert metrics.capability_denials == 0
        assert metrics.policy_denials == 0
        assert metrics.total_latency_ms == 0.0
        assert metrics.avg_latency_ms == 0.0

    def test_metrics_count_approvals(self, engine, registry, policies):
        """Metrics correctly count approved decisions."""
        setup_allow(registry, policies, agent_id="a1")
        setup_allow(registry, policies, agent_id="a2")
        
        engine.evaluate(make_request(agent_id="a1"))
        engine.evaluate(make_request(agent_id="a2"))
        
        metrics = engine.get_metrics()
        assert metrics.total_decisions == 2
        assert metrics.approved_count == 2
        assert metrics.denied_count == 0
        assert metrics.denied_count == 0

    def test_metrics_count_denials(self, engine):
        """Metrics correctly count denied decisions."""
        engine.evaluate(make_request(agent_id="a1"))
        engine.evaluate(make_request(agent_id="a2"))
        
        metrics = engine.get_metrics()
        assert metrics.total_decisions == 2
        assert metrics.denied_count == 2
        assert metrics.approved_count == 0

    def test_metrics_capability_denials(self, engine):
        """Metrics distinguish capability-stage denials."""
        # No capability registered → capability denial
        engine.evaluate(make_request())
        
        metrics = engine.get_metrics()
        assert metrics.capability_denials >= 1
        assert metrics.denied_count >= 1

    def test_metrics_policy_denials(self, engine, registry, policies):
        """Metrics distinguish policy-stage denials."""
        # Grant capability but add deny policy → policy denial
        cap = Capability(
            id="cap-1",
            name="Test",
            description="",
            action_types=["tool_call"],
            target_patterns=["*"],
        )
        registry.register(cap)
        registry.grant("agent-1", "cap-1")
        
        policies.add_policy(Policy(
            id="pol-deny",
            name="Deny all",
            description="",
            effect=PolicyEffect.DENY,
            conditions=[],
        ))
        
        engine.evaluate(make_request())
        
        metrics = engine.get_metrics()
        assert metrics.policy_denials >= 1
        assert metrics.denied_count >= 1

    def test_metrics_latency_recorded(self, engine, registry, policies):
        """Metrics record latency for decisions."""
        setup_allow(registry, policies)
        
        engine.evaluate(make_request())
        engine.evaluate(make_request())
        
        metrics = engine.get_metrics()
        assert metrics.total_latency_ms > 0
        assert metrics.avg_latency_ms > 0
        assert metrics.avg_latency_ms <= metrics.total_latency_ms

    def test_metrics_average_calculation(self, engine, registry, policies):
        """Average latency is correctly calculated."""
        setup_allow(registry, policies)
        
        for _ in range(5):
            engine.evaluate(make_request())
        
        metrics = engine.get_metrics()
        assert metrics.total_decisions == 5
        # Average should be total divided by count
        expected_avg = metrics.total_latency_ms / 5
        assert abs(metrics.avg_latency_ms - expected_avg) < 0.01

    def test_reset_metrics(self, engine, registry, policies):
        """Metrics can be reset to zero."""
        setup_allow(registry, policies)
        
        engine.evaluate(make_request())
        engine.evaluate(make_request())
        
        metrics = engine.get_metrics()
        assert metrics.total_decisions == 2
        
        engine.reset_metrics()
        
        metrics = engine.get_metrics()
        assert metrics.total_decisions == 0
        assert metrics.approved_count == 0
        assert metrics.total_latency_ms == 0.0

    def test_metrics_accumulate_across_decisions(self, engine, registry, policies):
        """Metrics accumulate correctly across many decisions."""
        # Grant capability and policy to multiple agents
        for i in range(3):
            setup_allow(registry, policies, agent_id=f"agent-{i}")
        
        # Make some approved decisions
        for i in range(3):
            engine.evaluate(make_request(agent_id=f"agent-{i}"))
        
        metrics_after_3 = engine.get_metrics()
        assert metrics_after_3.total_decisions == 3
        assert metrics_after_3.approved_count == 3
        assert metrics_after_3.denied_count == 0
        
        # Make some denied decisions
        engine.reset_metrics()
        for i in range(2):
            engine.evaluate(make_request(agent_id=f"unknown-{i}"))
        
        metrics_after_denials = engine.get_metrics()
        assert metrics_after_denials.total_decisions == 2
        assert metrics_after_denials.denied_count == 2
        assert metrics_after_denials.approved_count == 0
