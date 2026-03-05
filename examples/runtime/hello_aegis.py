"""Minimal end-to-end AEGIS hello-world demo.

This example shows:
1. Capability registration and grant
2. Policy registration
3. Tool registration through ToolProxy
4. Approved and denied tool calls
5. Audit records emitted by governance
"""

from pathlib import Path
import sys


# Allow running directly from repository root without package install.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "aegis-runtime"))

from aegis import AEGISRuntime, ActionType, Capability, Policy, PolicyEffect  # noqa: E402


def main() -> None:
    with AEGISRuntime() as runtime:
        runtime.capabilities.register(
            Capability(
                id="cap-echo-only",
                name="Echo tool capability",
                description="Allows only the echo_tool target",
                action_types=[ActionType.TOOL_CALL.value],
                target_patterns=["echo_tool"],
            )
        )
        runtime.capabilities.grant("agent-hello", "cap-echo-only")

        runtime.policies.add_policy(
            Policy(
                id="allow-tools",
                name="Allow tool calls",
                description="Allow governed tool calls once capability matches",
                effect=PolicyEffect.ALLOW,
                conditions=[],
            )
        )

        proxy = runtime.create_tool_proxy("agent-hello", "session-hello")
        proxy.register_tool(
            "echo",
            fn=lambda message: f"echo_tool -> {message}",
            target="echo_tool",
        )
        proxy.register_tool(
            "secret_read",
            fn=lambda: "top-secret",
            target="restricted_tool",
        )

        print("[ALLOW] calling echo...")
        allowed_result = proxy.call("echo", message="Hello AEGIS")
        print(f"  result: {allowed_result}")

        print("[DENY] calling secret_read...")
        try:
            proxy.call("secret_read")
        except PermissionError as exc:
            print(f"  denied: {exc}")

        history = runtime.audit.get_agent_history("agent-hello", limit=5)
        print("[AUDIT] recent records:")
        for record in reversed(history):
            print(
                f"  decision={record.decision} target={record.action_target} "
                f"reason={record.reason}"
            )


if __name__ == "__main__":
    main()