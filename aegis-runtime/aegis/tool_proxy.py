"""Tool Proxy Layer.

The Tool Proxy sits between an AI agent and the tools it wishes to
invoke.  Every tool call is intercepted and a governance request is
submitted to the :class:`~aegis.gateway.GovernanceGateway` before the
actual tool function is executed.

If the gateway returns ``Decision.DENIED`` or ``Decision.DEFERRED``,
the tool is **not** invoked and a :class:`PermissionError` is raised so
that the calling agent can handle the rejection cleanly.

Usage::

    proxy = ToolProxy(gateway, agent_id="agent-1", session_id="sess-abc")

    # Register a tool under a governance target name
    proxy.register_tool("read_file", fn=open_file_fn, target="fs://read")

    # This call is transparently governed
    result = proxy.call("read_file", path="/etc/hosts")
"""

from __future__ import annotations

from typing import Any, Callable

from .gateway import GovernanceGateway
from .protocol import AGPAction, AGPContext, AGPRequest, ActionType, Decision


class ToolProxy:
    """Interposes governance checks on every tool invocation.

    Parameters
    ----------
    gateway:
        The :class:`~aegis.gateway.GovernanceGateway` through which all
        tool calls are governed.
    agent_id:
        Identifier of the AI agent that owns this proxy.
    session_id:
        Identifier of the current agent session.
    """

    def __init__(
        self,
        gateway: GovernanceGateway,
        agent_id: str,
        session_id: str,
    ) -> None:
        self._gateway = gateway
        self._agent_id = agent_id
        self._session_id = session_id
        # name -> (callable, governance_target)
        self._tools: dict[str, tuple[Callable[..., Any], str]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_tool(
        self,
        name: str,
        fn: Callable[..., Any],
        target: str = "",
    ) -> None:
        """Register a tool with the proxy.

        Parameters
        ----------
        name:
            The logical name by which the tool is invoked.
        fn:
            The callable that implements the tool.
        target:
            The governance target string submitted in the AGP request.
            Defaults to *name* if not provided.
        """
        self._tools[name] = (fn, target or name)

    def unregister_tool(self, name: str) -> None:
        """Remove a tool registration (no-op if not registered)."""
        self._tools.pop(name, None)

    def registered_tools(self) -> list[str]:
        """Return the names of all registered tools."""
        return list(self._tools.keys())

    # ------------------------------------------------------------------
    # Invocation
    # ------------------------------------------------------------------

    def call(self, tool_name: str, **kwargs: Any) -> Any:
        """Invoke *tool_name* subject to governance approval.

        The method constructs an :class:`~aegis.protocol.AGPRequest` with
        ``action.type = ActionType.TOOL_CALL``, submits it to the gateway,
        and only executes the tool if the decision is ``APPROVED``.

        Parameters
        ----------
        tool_name:
            Name of the previously registered tool.
        **kwargs:
            Keyword arguments forwarded to the tool callable.

        Returns
        -------
        Any
            The return value of the tool callable.

        Raises
        ------
        ValueError
            If *tool_name* has not been registered.
        PermissionError
            If the governance decision is not ``APPROVED``.
        """
        if tool_name not in self._tools:
            raise ValueError(
                f"Tool '{tool_name}' is not registered with this ToolProxy."
            )

        fn, target = self._tools[tool_name]

        request = AGPRequest(
            agent_id=self._agent_id,
            action=AGPAction(
                type=ActionType.TOOL_CALL,
                target=target,
                parameters=dict(kwargs),
            ),
            context=AGPContext(session_id=self._session_id),
        )

        response = self._gateway.submit(request)

        if response.decision != Decision.APPROVED:
            raise PermissionError(
                f"Tool call '{tool_name}' was {response.decision.value} by AEGIS: "
                f"{response.reason} (audit_id={response.audit_id})"
            )

        return fn(**kwargs)
