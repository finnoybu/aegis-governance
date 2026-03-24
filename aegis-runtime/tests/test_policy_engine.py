"""Tests for the PolicyEngine."""

import pytest

from aegis.exceptions import AEGISPolicyError
from aegis.policy_engine import (
    Policy,
    PolicyCondition,
    PolicyEffect,
    PolicyEngine,
    PolicyResult,
)
from aegis.protocol import AGPAction, AGPContext, AGPRequest, ActionType, Decision


def make_request(agent_id: str = "agent-1", action_type: ActionType = ActionType.TOOL_CALL,
                 target: str = "my_tool") -> AGPRequest:
    return AGPRequest(
        agent_id=agent_id,
        action=AGPAction(type=action_type, target=target),
        context=AGPContext(session_id="sess-1"),
    )


def always_true(_req: AGPRequest) -> bool:
    return True


def always_false(_req: AGPRequest) -> bool:
    return False


def make_allow_policy(policy_id: str = "pol-allow", priority: int = 200) -> Policy:
    return Policy(
        id=policy_id,
        name="Allow All",
        description="Allows everything",
        effect=PolicyEffect.ALLOW,
        conditions=[PolicyCondition(evaluate=always_true, description="always true")],
        priority=priority,
    )


def make_deny_policy(policy_id: str = "pol-deny", priority: int = 100) -> Policy:
    return Policy(
        id=policy_id,
        name="Deny All",
        description="Denies everything",
        effect=PolicyEffect.DENY,
        conditions=[PolicyCondition(evaluate=always_true, description="always true")],
        priority=priority,
    )


@pytest.fixture()
def engine() -> PolicyEngine:
    return PolicyEngine()


class TestPolicyManagement:
    def test_add_and_retrieve(self, engine):
        policy = make_allow_policy()
        engine.add_policy(policy)
        assert engine.get_policy("pol-allow") is policy

    def test_duplicate_policy_raises(self, engine):
        engine.add_policy(make_allow_policy())
        with pytest.raises(ValueError, match="already registered"):
            engine.add_policy(make_allow_policy())

    def test_remove_policy(self, engine):
        engine.add_policy(make_allow_policy())
        engine.remove_policy("pol-allow")
        assert engine.get_policy("pol-allow") is None

    def test_list_policies_sorted_by_priority(self, engine):
        engine.add_policy(make_allow_policy("p1", priority=300))
        engine.add_policy(make_deny_policy("p2", priority=100))
        ids = [p.id for p in engine.list_policies()]
        assert ids == ["p2", "p1"]


class TestDefaultDeny:
    def test_no_policies_means_denied(self, engine):
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED
        assert "default-deny" in result.reason

    def test_no_matching_policy_means_denied(self, engine):
        engine.add_policy(Policy(
            id="pol-never-match",
            name="Never Match",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[PolicyCondition(evaluate=always_false, description="always false")],
        ))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED


class TestAllowPolicy:
    def test_matching_allow_approves(self, engine):
        engine.add_policy(make_allow_policy())
        result = engine.evaluate(make_request())
        assert result.decision == Decision.APPROVED
        assert "Allow All" in result.reason


class TestDenyPolicy:
    def test_matching_deny_denies(self, engine):
        engine.add_policy(make_deny_policy())
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED
        assert "Deny All" in result.reason

    def test_deny_overrides_allow_when_higher_priority(self, engine):
        # Deny has priority=50 (evaluated first), allow has priority=200
        engine.add_policy(make_allow_policy("pol-allow", priority=200))
        engine.add_policy(make_deny_policy("pol-deny", priority=50))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED

    def test_allow_wins_when_deny_does_not_match(self, engine):
        # Deny condition never matches
        engine.add_policy(Policy(
            id="pol-deny",
            name="Deny (no match)",
            description="",
            effect=PolicyEffect.DENY,
            conditions=[PolicyCondition(evaluate=always_false, description="always false")],
            priority=50,
        ))
        engine.add_policy(make_allow_policy())
        result = engine.evaluate(make_request())
        assert result.decision == Decision.APPROVED


class TestDisabledPolicy:
    def test_disabled_policy_is_skipped(self, engine):
        policy = make_allow_policy()
        policy.enabled = False
        engine.add_policy(policy)
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED  # default-deny because policy skipped


class TestEvaluationTrace:
    def test_evaluations_returned(self, engine):
        engine.add_policy(make_allow_policy())
        result = engine.evaluate(make_request())
        assert len(result.evaluations) == 1
        ev = result.evaluations[0]
        assert ev.policy_id == "pol-allow"
        assert ev.matched is True
        assert ev.effect == "allow"

    def test_deny_stops_evaluation_early(self, engine):
        # Deny is at priority=50, allow at 200. After deny matches, we stop.
        engine.add_policy(make_allow_policy("pol-allow", priority=200))
        engine.add_policy(make_deny_policy("pol-deny", priority=50))
        result = engine.evaluate(make_request())
        # Only the deny policy should be in evaluations (we stopped after match)
        assert result.evaluations[-1].policy_id == "pol-deny"
        assert result.evaluations[-1].matched is True


class TestConditionError:
    def test_condition_exception_raises_policy_error(self, engine):
        def bad_condition(_req):
            raise RuntimeError("oops")

        engine.add_policy(Policy(
            id="bad-pol",
            name="Bad",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[PolicyCondition(evaluate=bad_condition, description="bad")],
        ))
        with pytest.raises(AEGISPolicyError, match="oops"):
            engine.evaluate(make_request())


class TestConditionalPolicy:
    def test_agent_specific_allow(self, engine):
        engine.add_policy(Policy(
            id="pol-agent-specific",
            name="Allow agent-A only",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[
                PolicyCondition(
                    evaluate=lambda req: req.agent_id == "agent-A",
                    description="agent is agent-A",
                )
            ],
        ))
        assert engine.evaluate(make_request(agent_id="agent-A")).decision == Decision.APPROVED
        assert engine.evaluate(make_request(agent_id="agent-B")).decision == Decision.DENIED


class TestValidatePolicy:
    """Test policy validation."""

    def test_valid_policy_passes(self, engine):
        policy = make_allow_policy()
        engine.validate_policy(policy)  # Should not raise

    def test_empty_policy_id_raises(self, engine):
        with pytest.raises(AEGISPolicyError, match="id must not be empty"):
            engine.validate_policy(Policy(
                id="",
                name="Test",
                description="",
                effect=PolicyEffect.ALLOW,
                conditions=[],
            ))

    def test_empty_policy_name_raises(self, engine):
        with pytest.raises(AEGISPolicyError, match="name must not be empty"):
            engine.validate_policy(Policy(
                id="pol-1",
                name="",
                description="",
                effect=PolicyEffect.ALLOW,
                conditions=[],
            ))

    def test_invalid_effect_raises(self, engine):
        policy = make_allow_policy()
        policy.effect = "invalid"  # type: ignore
        with pytest.raises(AEGISPolicyError, match="must be ALLOW, DENY, ESCALATE, or REQUIRE_CONFIRMATION"):
            engine.validate_policy(policy)

    def test_non_callable_condition_raises(self, engine):
        with pytest.raises(AEGISPolicyError, match="not callable"):
            engine.validate_policy(Policy(
                id="pol-1",
                name="Bad condition",
                description="",
                effect=PolicyEffect.ALLOW,
                conditions=[PolicyCondition(evaluate="not callable", description="bad")],  # type: ignore
            ))

    def test_empty_condition_description_raises(self, engine):
        with pytest.raises(AEGISPolicyError, match="description must not be empty"):
            engine.validate_policy(Policy(
                id="pol-1",
                name="Test",
                description="",
                effect=PolicyEffect.ALLOW,
                conditions=[PolicyCondition(evaluate=always_true, description="")],
            ))

    def test_add_policy_validates(self, engine):
        """Test that add_policy calls validate_policy."""
        with pytest.raises(AEGISPolicyError):
            engine.add_policy(Policy(
                id="",  # Invalid
                name="Test",
                description="",
                effect=PolicyEffect.ALLOW,
                conditions=[],
            ))


class TestFindPoliciesByEffect:
    """Test finding policies by effect type."""

    def test_find_all_allow_policies(self, engine):
        engine.add_policy(make_allow_policy("p1", priority=100))
        engine.add_policy(make_allow_policy("p2", priority=200))
        engine.add_policy(make_deny_policy("p3", priority=50))
        
        allow_policies = engine.find_policies_by_effect(PolicyEffect.ALLOW)
        assert len(allow_policies) == 2
        assert [p.id for p in allow_policies] == ["p1", "p2"]  # Sorted by priority

    def test_find_all_deny_policies(self, engine):
        engine.add_policy(make_allow_policy("p1"))
        engine.add_policy(make_deny_policy("p2", priority=100))
        engine.add_policy(make_deny_policy("p3", priority=50))
        
        deny_policies = engine.find_policies_by_effect(PolicyEffect.DENY)
        assert len(deny_policies) == 2
        assert [p.id for p in deny_policies] == ["p3", "p2"]  # Sorted by priority

    def test_no_matching_effect_returns_empty(self, engine):
        engine.add_policy(make_allow_policy())
        deny_policies = engine.find_policies_by_effect(PolicyEffect.DENY)
        assert deny_policies == []


class TestFindMatchingPolicies:
    """Test finding policies that match a request."""

    def test_find_matching_policies(self, engine):
        # Only p1 will match this request
        engine.add_policy(Policy(
            id="p1",
            name="Match agent-1",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[
                PolicyCondition(
                    evaluate=lambda req: req.agent_id == "agent-1",
                    description="agent is agent-1",
                )
            ],
        ))
        engine.add_policy(Policy(
            id="p2",
            name="Match agent-2",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[
                PolicyCondition(
                    evaluate=lambda req: req.agent_id == "agent-2",
                    description="agent is agent-2",
                )
            ],
        ))
        
        matching = engine.find_matching_policies(make_request(agent_id="agent-1"))
        assert len(matching) == 1
        assert matching[0].id == "p1"

    def test_find_matching_multiple(self, engine):
        # Both policies will match
        engine.add_policy(Policy(
            id="p1",
            name="Always true 1",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[PolicyCondition(evaluate=always_true, description="always matches")],
        ))
        engine.add_policy(Policy(
            id="p2",
            name="Always true 2",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[PolicyCondition(evaluate=always_true, description="always matches")],
        ))
        
        matching = engine.find_matching_policies(make_request())
        assert len(matching) == 2

    def test_find_matching_skips_disabled(self, engine):
        policy = make_allow_policy("p1")
        policy.enabled = False
        engine.add_policy(policy)
        engine.add_policy(make_allow_policy("p2"))
        
        matching = engine.find_matching_policies(make_request())
        assert len(matching) == 1
        assert matching[0].id == "p2"

    def test_find_matching_sorted_by_priority(self, engine):
        engine.add_policy(make_allow_policy("p1", priority=300))
        engine.add_policy(make_allow_policy("p2", priority=100))
        
        matching = engine.find_matching_policies(make_request())
        assert [p.id for p in matching] == ["p2", "p1"]


# ── ESCALATE and REQUIRE_CONFIRMATION tests ─────────────────────


def make_escalate_policy(policy_id: str = "pol-escalate", priority: int = 150) -> Policy:
    return Policy(
        id=policy_id,
        name="Escalate High Risk",
        description="Escalates high-risk actions",
        effect=PolicyEffect.ESCALATE,
        conditions=[PolicyCondition(evaluate=always_true, description="always true")],
        priority=priority,
    )


def make_require_confirmation_policy(policy_id: str = "pol-confirm", priority: int = 175) -> Policy:
    return Policy(
        id=policy_id,
        name="Require Confirmation",
        description="Requires human confirmation",
        effect=PolicyEffect.REQUIRE_CONFIRMATION,
        conditions=[PolicyCondition(evaluate=always_true, description="always true")],
        priority=priority,
    )


class TestEscalatePolicy:
    def test_matching_escalate_returns_escalate(self):
        engine = PolicyEngine()
        engine.add_policy(make_escalate_policy())
        result = engine.evaluate(make_request())
        assert result.decision == Decision.ESCALATE

    def test_deny_overrides_escalate(self):
        engine = PolicyEngine()
        engine.add_policy(make_escalate_policy(priority=200))
        engine.add_policy(make_deny_policy(priority=100))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED

    def test_escalate_overrides_allow(self):
        engine = PolicyEngine()
        engine.add_policy(make_allow_policy(priority=100))
        engine.add_policy(make_escalate_policy(priority=200))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.ESCALATE


class TestRequireConfirmationPolicy:
    def test_matching_require_confirmation(self):
        engine = PolicyEngine()
        engine.add_policy(make_require_confirmation_policy())
        result = engine.evaluate(make_request())
        assert result.decision == Decision.REQUIRE_CONFIRMATION

    def test_deny_overrides_require_confirmation(self):
        engine = PolicyEngine()
        engine.add_policy(make_require_confirmation_policy(priority=200))
        engine.add_policy(make_deny_policy(priority=100))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED

    def test_escalate_overrides_require_confirmation(self):
        engine = PolicyEngine()
        engine.add_policy(make_require_confirmation_policy(priority=100))
        engine.add_policy(make_escalate_policy(priority=200))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.ESCALATE

    def test_require_confirmation_overrides_allow(self):
        engine = PolicyEngine()
        engine.add_policy(make_allow_policy(priority=100))
        engine.add_policy(make_require_confirmation_policy(priority=200))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.REQUIRE_CONFIRMATION


class TestFullPrecedenceChain:
    def test_deny_wins_over_all(self):
        engine = PolicyEngine()
        engine.add_policy(make_allow_policy(priority=100))
        engine.add_policy(make_require_confirmation_policy(priority=150))
        engine.add_policy(make_escalate_policy(priority=200))
        engine.add_policy(make_deny_policy(priority=50))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.DENIED

    def test_escalate_wins_over_confirm_and_allow(self):
        engine = PolicyEngine()
        engine.add_policy(make_allow_policy(priority=100))
        engine.add_policy(make_require_confirmation_policy(priority=150))
        engine.add_policy(make_escalate_policy(priority=200))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.ESCALATE

    def test_confirm_wins_over_allow(self):
        engine = PolicyEngine()
        engine.add_policy(make_allow_policy(priority=100))
        engine.add_policy(make_require_confirmation_policy(priority=200))
        result = engine.evaluate(make_request())
        assert result.decision == Decision.REQUIRE_CONFIRMATION

    def test_allow_wins_when_only_option(self):
        engine = PolicyEngine()
        engine.add_policy(make_allow_policy())
        result = engine.evaluate(make_request())
        assert result.decision == Decision.APPROVED
