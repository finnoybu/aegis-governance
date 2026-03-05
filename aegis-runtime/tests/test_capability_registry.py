"""Tests for the CapabilityRegistry."""

from datetime import datetime, timedelta, timezone

import pytest

from aegis.capability_registry import Capability, CapabilityRegistry
from aegis.exceptions import AEGISCapabilityError


@pytest.fixture()
def registry() -> CapabilityRegistry:
    return CapabilityRegistry()


def make_cap(
    cap_id: str = "cap-1",
    action_types: list[str] | None = None,
    target_patterns: list[str] | None = None,
    expires_at: datetime | None = None,
) -> Capability:
    return Capability(
        id=cap_id,
        name="Test Capability",
        description="For testing",
        action_types=action_types or ["tool_call"],
        target_patterns=target_patterns or ["*"],
        expires_at=expires_at,
    )


class TestCapabilityIsActive:
    def test_no_expiry_is_active(self):
        assert make_cap().is_active()

    def test_future_expiry_is_active(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        assert make_cap(expires_at=future).is_active()

    def test_past_expiry_is_not_active(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        assert not make_cap(expires_at=past).is_active()


class TestCapabilityCovers:
    def test_matching_action_and_wildcard_target(self):
        cap = make_cap(action_types=["tool_call"], target_patterns=["*"])
        assert cap.covers("tool_call", "anything")

    def test_wrong_action_type(self):
        cap = make_cap(action_types=["file_read"], target_patterns=["*"])
        assert not cap.covers("tool_call", "anything")

    def test_glob_pattern_matches(self):
        cap = make_cap(action_types=["file_read"], target_patterns=["/docs/*"])
        assert cap.covers("file_read", "/docs/readme.md")
        assert not cap.covers("file_read", "/etc/hosts")

    def test_expired_capability_never_covers(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        cap = make_cap(expires_at=past, action_types=["tool_call"], target_patterns=["*"])
        assert not cap.covers("tool_call", "anything")


class TestRegistryRegister:
    def test_register_and_retrieve(self, registry):
        cap = make_cap()
        registry.register(cap)
        assert registry.get_capability("cap-1") is cap

    def test_duplicate_raises(self, registry):
        registry.register(make_cap())
        with pytest.raises(ValueError, match="already registered"):
            registry.register(make_cap())

    def test_unregister(self, registry):
        registry.register(make_cap())
        registry.unregister("cap-1")
        assert registry.get_capability("cap-1") is None


class TestRegistryGrant:
    def test_grant_known_capability(self, registry):
        registry.register(make_cap())
        registry.grant("agent-1", "cap-1")
        caps = registry.get_agent_capabilities("agent-1")
        assert len(caps) == 1
        assert caps[0].id == "cap-1"

    def test_grant_unknown_capability_raises(self, registry):
        with pytest.raises(AEGISCapabilityError, match="Cannot grant unknown"):
            registry.grant("agent-1", "nonexistent")

    def test_revoke(self, registry):
        registry.register(make_cap())
        registry.grant("agent-1", "cap-1")
        registry.revoke("agent-1", "cap-1")
        assert registry.get_agent_capabilities("agent-1") == []

    def test_revoke_all(self, registry):
        cap_a = make_cap("cap-a")
        cap_b = make_cap("cap-b")
        registry.register(cap_a)
        registry.register(cap_b)
        registry.grant("agent-1", "cap-a")
        registry.grant("agent-1", "cap-b")
        registry.revoke_all("agent-1")
        assert registry.get_agent_capabilities("agent-1") == []

    def test_bulk_grant(self, registry):
        """Test bulk grant of single capability to multiple agents."""
        registry.register(make_cap())
        agent_ids = ["agent-1", "agent-2", "agent-3"]
        count = registry.bulk_grant(agent_ids, "cap-1")
        assert count == 3
        for agent_id in agent_ids:
            assert registry.has_capability_for_action(agent_id, "tool_call", "anything")

    def test_bulk_grant_unknown_capability_raises(self, registry):
        """Test that bulk_grant raises for unknown capability."""
        with pytest.raises(AEGISCapabilityError, match="Cannot grant unknown"):
            registry.bulk_grant(["agent-1"], "nonexistent")

    def test_bulk_grant_idempotent(self, registry):
        """Test that bulk_grant doesn't duplicate if already granted."""
        registry.register(make_cap())
        registry.grant("agent-1", "cap-1")
        count = registry.bulk_grant(["agent-1", "agent-2"], "cap-1")
        # agent-1 already had it, so only agent-2 is new
        assert count == 1

    def test_bulk_revoke(self, registry):
        """Test bulk revoke of single capability from multiple agents."""
        registry.register(make_cap())
        agent_ids = ["agent-1", "agent-2", "agent-3"]
        for agent_id in agent_ids:
            registry.grant(agent_id, "cap-1")
        count = registry.bulk_revoke(agent_ids, "cap-1")
        assert count == 3
        for agent_id in agent_ids:
            assert not registry.has_capability_for_action(agent_id, "tool_call", "anything")

    def test_bulk_revoke_partial(self, registry):
        """Test bulk revoke when only some agents have the capability."""
        registry.register(make_cap())
        registry.grant("agent-1", "cap-1")
        # agent-2 doesn't have cap-1
        count = registry.bulk_revoke(["agent-1", "agent-2"], "cap-1")
        assert count == 1

    def test_thread_safe_concurrent_grants(self, registry):
        """Test that concurrent grant operations are thread-safe."""
        import threading
        registry.register(make_cap())
        
        def grant_agent(agent_id):
            registry.grant(agent_id, "cap-1")
        
        threads = [
            threading.Thread(target=grant_agent, args=(f"agent-{i}",))
            for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All agents should have the capability
        for i in range(10):
            assert registry.has_capability_for_action(f"agent-{i}", "tool_call", "anything")


class TestHasCapabilityForAction:
    def test_agent_with_capability(self, registry):
        registry.register(make_cap(action_types=["tool_call"], target_patterns=["*"]))
        registry.grant("agent-1", "cap-1")
        assert registry.has_capability_for_action("agent-1", "tool_call", "any_tool")

    def test_agent_without_capability(self, registry):
        assert not registry.has_capability_for_action("agent-1", "tool_call", "tool")

    def test_expired_capability_not_counted(self, registry):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        registry.register(make_cap(expires_at=past))
        registry.grant("agent-1", "cap-1")
        assert not registry.has_capability_for_action("agent-1", "tool_call", "tool")

    def test_unregistered_capability_removed_also_clears(self, registry):
        registry.register(make_cap())
        registry.grant("agent-1", "cap-1")
        registry.unregister("cap-1")
        assert not registry.has_capability_for_action("agent-1", "tool_call", "tool")
