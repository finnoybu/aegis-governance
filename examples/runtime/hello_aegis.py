from aegis import (
    AEGISRuntime,
    Capability,
    Policy,
    PolicyEffect,
    ActionType
)

runtime = AEGISRuntime()

# Register capability
runtime.capabilities.register(
    Capability(
        id="cap-read-docs",
        name="Read documentation",
        description="Allows reading files in /docs",
        action_types=[ActionType.FILE_READ.value],
        target_patterns=["/docs/*"]
    )
)

# Grant capability to agent
runtime.capabilities.grant("agent-1", "cap-read-docs")

# Allow policy
runtime.policies.add_policy(
    Policy(
        id="allow-docs",
        name="Allow documentation reads",
        description="Agents with docs capability may read documentation",
        effect=PolicyEffect.ALLOW,
        conditions=[]
    )
)

proxy = runtime.create_tool_proxy("agent-1", "session-1")

proxy.register_tool(
    "read_file",
    fn=lambda path: open(path).read(),
    target="/docs/read"
)

print("AEGIS runtime initialized successfully.")