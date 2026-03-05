"""Integration tests for the full AEGIS governance pipeline.

These tests exercise all components working together end-to-end,
matching realistic usage patterns described in the problem statement.
"""

from __future__ import annotations

import pytest

from aegis import AEGISRuntime
from aegis.capability_registry import Capability
from aegis.policy_engine import Policy, PolicyCondition, PolicyEffect
from aegis.protocol import ActionType, Decision


def make_runtime_with_agent(
    agent_id: str = "agent-1",
    action_types: list[str] | None = None,
    target_patterns: list[str] | None = None,
) -> AEGISRuntime:
    rt = AEGISRuntime()
    cap = Capability(
        id="cap-default",
        name="Default",
        description="",
        action_types=action_types or ["tool_call"],
        target_patterns=target_patterns or ["*"],
    )
    rt.capabilities.register(cap)
    rt.capabilities.grant(agent_id, "cap-default")
    rt.policies.add_policy(Policy(
        id="pol-allow-default",
        name="Allow by default",
        description="",
        effect=PolicyEffect.ALLOW,
        conditions=[],
    ))
    return rt


class TestDefaultDenyPosture:
    """Without any configuration, every action must be denied."""

    def test_unconfigured_runtime_denies_everything(self):
        rt = AEGISRuntime()
        proxy = rt.create_tool_proxy("agent-x", "sess-1")
        proxy.register_tool("tool", fn=lambda: None, target="tool")
        with pytest.raises(PermissionError):
            proxy.call("tool")


class TestCapabilityBasedAccess:
    """Capabilities restrict which actions agents are allowed to attempt."""

    def test_agent_without_capability_is_denied(self):
        rt = AEGISRuntime()
        # Register capability but do NOT grant it
        rt.capabilities.register(Capability(
            id="cap-1", name="X", description="",
            action_types=["tool_call"], target_patterns=["*"],
        ))
        rt.policies.add_policy(Policy(
            id="pol", name="Allow all", description="",
            effect=PolicyEffect.ALLOW, conditions=[],
        ))
        proxy = rt.create_tool_proxy("agent-no-cap", "sess")
        proxy.register_tool("t", fn=lambda: None, target="t")
        with pytest.raises(PermissionError):
            proxy.call("t")

    def test_revoked_capability_denies_subsequent_calls(self):
        rt = make_runtime_with_agent()
        proxy = rt.create_tool_proxy("agent-1", "sess-1")
        proxy.register_tool("t", fn=lambda: "ok", target="t")
        assert proxy.call("t") == "ok"

        rt.capabilities.revoke("agent-1", "cap-default")
        with pytest.raises(PermissionError):
            proxy.call("t")

    def test_target_scoped_capability(self):
        rt = AEGISRuntime()
        rt.capabilities.register(Capability(
            id="cap-docs", name="Docs", description="",
            action_types=["file_read"], target_patterns=["/docs/*"],
        ))
        rt.capabilities.grant("agent-1", "cap-docs")
        rt.policies.add_policy(Policy(
            id="pol", name="Allow", description="",
            effect=PolicyEffect.ALLOW, conditions=[],
        ))

        from aegis.protocol import AGPAction, AGPContext, AGPRequest

        def submit(target: str) -> Decision:
            return rt.gateway.submit(AGPRequest(
                agent_id="agent-1",
                action=AGPAction(type=ActionType.FILE_READ, target=target),
                context=AGPContext(session_id="sess"),
            )).decision

        assert submit("/docs/intro.md") == Decision.APPROVED
        assert submit("/etc/passwd") == Decision.DENIED


class TestPolicyEnforcement:
    """Policy rules are evaluated deterministically and in priority order."""

    def test_high_priority_deny_blocks_low_priority_allow(self):
        rt = make_runtime_with_agent()
        rt.policies.add_policy(Policy(
            id="pol-deny-shell",
            name="Block shell exec",
            description="",
            effect=PolicyEffect.DENY,
            priority=0,
            conditions=[
                PolicyCondition(
                    evaluate=lambda req: req.action.type == ActionType.TOOL_CALL,
                    description="is tool call",
                )
            ],
        ))
        proxy = rt.create_tool_proxy("agent-1", "sess")
        proxy.register_tool("t", fn=lambda: "value", target="t")
        with pytest.raises(PermissionError, match="denied"):
            proxy.call("t")

    def test_conditional_policy_only_affects_target_agent(self):
        rt = AEGISRuntime()
        cap = Capability(
            id="cap", name="", description="",
            action_types=["tool_call"], target_patterns=["*"],
        )
        rt.capabilities.register(cap)
        rt.capabilities.grant("agent-good", "cap")
        rt.capabilities.grant("agent-bad", "cap")

        rt.policies.add_policy(Policy(
            id="pol-deny-bad",
            name="Deny bad agent",
            description="",
            effect=PolicyEffect.DENY,
            priority=50,
            conditions=[
                PolicyCondition(
                    evaluate=lambda req: req.agent_id == "agent-bad",
                    description="is bad agent",
                )
            ],
        ))
        rt.policies.add_policy(Policy(
            id="pol-allow-all",
            name="Allow all",
            description="",
            effect=PolicyEffect.ALLOW,
            conditions=[],
            priority=200,
        ))

        from aegis.protocol import AGPAction, AGPContext, AGPRequest

        def submit(agent_id: str) -> Decision:
            return rt.gateway.submit(AGPRequest(
                agent_id=agent_id,
                action=AGPAction(type=ActionType.TOOL_CALL, target="t"),
                context=AGPContext(session_id="sess"),
            )).decision

        assert submit("agent-good") == Decision.APPROVED
        assert submit("agent-bad") == Decision.DENIED


class TestAuditTrail:
    """Every decision must produce an immutable audit record."""

    def test_every_decision_is_recorded(self):
        rt = make_runtime_with_agent()
        proxy = rt.create_tool_proxy("agent-1", "sess-1")
        proxy.register_tool("t", fn=lambda: None, target="t")
        proxy.call("t")  # approved
        # Trigger a denied call from another agent
        proxy2 = rt.create_tool_proxy("unknown-agent", "sess-2")
        proxy2.register_tool("t", fn=lambda: None, target="t")
        with pytest.raises(PermissionError):
            proxy2.call("t")

        assert len(rt.audit.get_agent_history("agent-1")) >= 1
        assert len(rt.audit.get_agent_history("unknown-agent")) >= 1

    def test_audit_records_are_immutable(self):
        rt = make_runtime_with_agent()
        from aegis.protocol import AGPAction, AGPContext, AGPRequest
        resp = rt.gateway.submit(AGPRequest(
            agent_id="agent-1",
            action=AGPAction(type=ActionType.TOOL_CALL, target="t"),
            context=AGPContext(session_id="s"),
        ))
        record = rt.audit.get_record(resp.audit_id)
        assert record is not None
        # AuditRecord is a frozen dataclass
        with pytest.raises((AttributeError, TypeError)):
            record.decision = "approved"  # type: ignore[misc]


class TestContextManager:
    """AEGISRuntime can be used as a context manager for resource cleanup."""

    def test_context_manager_usage(self):
        """Test that runtime can be used with 'with' statement."""
        with AEGISRuntime() as rt:
            assert rt is not None
            rt.policies.add_policy(Policy(
                id="pol", name="Allow all", description="",
                effect=PolicyEffect.ALLOW, conditions=[],
            ))

    def test_context_manager_calls_shutdown(self):
        """Test that exiting context manager triggers shutdown."""
        rt = AEGISRuntime()
        with rt:
            assert not rt._is_shutdown
        assert rt._is_shutdown

    def test_context_manager_with_exception(self):
        """Test that shutdown is called even if exception occurs."""
        rt = AEGISRuntime()
        try:
            with rt:
                raise ValueError("test error")
        except ValueError:
            pass
        assert rt._is_shutdown

    def test_shutdown_is_idempotent(self):
        """Test that calling shutdown multiple times is safe."""
        rt = AEGISRuntime()
        rt.shutdown()
        rt.shutdown()  # Should not raise
        assert rt._is_shutdown

    def test_runtime_works_normally_without_context_manager(self):
        """Test that runtime still works if not used with context manager."""
        rt = AEGISRuntime()
        rt.policies.add_policy(Policy(
            id="pol", name="Allow all", description="",
            effect=PolicyEffect.ALLOW, conditions=[],
        ))
        rt.shutdown()
        assert rt._is_shutdown

    def test_context_manager_with_full_workflow(self):
        """Test complete workflow using context manager."""
        with AEGISRuntime() as rt:
            # Register capability
            cap = Capability(
                id="cap-1",
                name="Test capability",
                description="",
                action_types=["tool_call"],
                target_patterns=["*"],
            )
            rt.capabilities.register(cap)
            rt.capabilities.grant("agent-1", "cap-1")
            
            # Add policy
            rt.policies.add_policy(Policy(
                id="pol-1",
                name="Allow all",
                description="",
                effect=PolicyEffect.ALLOW,
                conditions=[],
            ))
            
            # Create tool proxy and execute
            proxy = rt.create_tool_proxy("agent-1", "sess-1")
            proxy.register_tool("dummy", fn=lambda: "result", target="dummy")
            result = proxy.call("dummy")
            assert result == "result"
            
            # Verify audit trail
            assert rt.audit.record_count() > 0
