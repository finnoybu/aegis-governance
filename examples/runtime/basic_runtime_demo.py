"""Basic runtime governance demo.

Demonstrates policy-controlled allow/deny behavior through ToolProxy.
"""

from pathlib import Path
import sys


# Allow running directly from repository root without package install.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "aegis-runtime"))

from aegis import (  # noqa: E402
    AEGISRuntime,
    ActionType,
    Capability,
    Policy,
    PolicyCondition,
    PolicyEffect,
)


def main() -> None:
    with AEGISRuntime() as runtime:
        runtime.capabilities.register(
            Capability(
                id="cap-tool-all",
                name="Tool call capability",
                description="Allows tool_call targets via policy control",
                action_types=[ActionType.TOOL_CALL.value],
                target_patterns=["*"],
            )
        )
        runtime.capabilities.grant("agent-demo", "cap-tool-all")

        runtime.policies.add_policy(
            Policy(
                id="deny-sensitive-tool",
                name="Deny sensitive tool",
                description="Blocks sensitive_tool target",
                effect=PolicyEffect.DENY,
                conditions=[
                    PolicyCondition(
                        evaluate=lambda req: req.action.target == "sensitive_tool",
                        description="deny calls to sensitive_tool",
                    )
                ],
                priority=100,
            )
        )
        runtime.policies.add_policy(
            Policy(
                id="allow-all-tools",
                name="Allow all remaining tool calls",
                description="Fallback allow policy",
                effect=PolicyEffect.ALLOW,
                conditions=[],
                priority=200,
            )
        )

        proxy = runtime.create_tool_proxy("agent-demo", "session-demo")

        def safe_tool(message: str) -> str:
            return f"safe_tool executed: {message}"

        def sensitive_tool() -> str:
            return "sensitive operation executed"

        proxy.register_tool("safe_tool", safe_tool, target="safe_tool")
        proxy.register_tool("sensitive_tool", sensitive_tool, target="sensitive_tool")

        print("[ALLOW] calling safe_tool...")
        ok = proxy.call("safe_tool", message="Hello from AEGIS")
        print(f"  result: {ok}")

        print("[DENY] calling sensitive_tool...")
        try:
            proxy.call("sensitive_tool")
        except PermissionError as exc:
            print(f"  denied: {exc}")

        print("[AUDIT] session decisions:")
        for record in reversed(runtime.audit.get_session_history("session-demo")):
            print(
                f"  decision={record.decision} target={record.action_target} "
                f"policy_reason={record.reason}"
            )


if __name__ == "__main__":
    main()