from aegis import (
    AEGISRuntime,
    Capability,
    Policy,
    PolicyEffect,
    ActionType
)

runtime = AEGISRuntime()

runtime.capabilities.register(
    Capability(
        id="cap-demo",
        name="Demo Capability",
        description="Allows demo tool execution",
        action_types=[ActionType.TOOL_CALL.value],
        target_patterns=["demo_tool"]
    )
)

runtime.capabilities.grant("agent-demo", "cap-demo")

runtime.policies.add_policy(
    Policy(
        id="allow-demo",
        name="Allow demo tool",
        description="Permit demo tool execution",
        effect=PolicyEffect.ALLOW,
        conditions=[]
    )
)

proxy = runtime.create_tool_proxy("agent-demo", "session-demo")

def demo_tool(message: str):
    return f"Tool executed with message: {message}"

proxy.register_tool("demo_tool", demo_tool, target="demo_tool")

result = proxy.call("demo_tool", message="Hello from AEGIS")
print(result)