"""Tool Proxy Layer.

The Tool Proxy sits between an AI agent and the tools it wishes to
invoke.  Every tool call is intercepted and a governance request is
submitted to the :class:`~aegis.gateway.GovernanceGateway` before the
actual tool function is executed.

If the gateway returns ``Decision.DENIED`` or ``Decision.ESCALATE``,
the tool is **not** invoked and a :class:`PermissionError` is raised so
that the calling agent can handle the rejection cleanly.

Supports synchronous and asynchronous tool invocation, with optional
timeouts and call history tracking.

Usage::

    proxy = ToolProxy(gateway, agent_id="agent-1", session_id="sess-abc")

    # Register a tool under a governance target name
    proxy.register_tool("read_file", fn=open_file_fn, target="fs://read")

    # Synchronous call (transparently governed)
    result = proxy.call("read_file", path="/etc/hosts")
    
    # Async call with timeout
    result = await proxy.async_call("slow_tool", timeout=5.0)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .gateway import GovernanceGateway
from .protocol import AGPAction, AGPContext, AGPRequest, ActionType, Decision


@dataclass(frozen=True)
class CallRecord:
    """Record of a single tool invocation.
    
    Parameters
    ----------
    tool_name : str
        The name of the tool that was invoked.
    timestamp : float
        Unix timestamp of the call.
    duration_ms : float
        Duration of the call in milliseconds.
    decision : str
        The governance decision (approved, denied, etc.).
    approved : bool
        Whether the call was approved.
    error : str or None
        Exception message if the call failed, None otherwise.
    """
    
    tool_name: str
    timestamp: float
    duration_ms: float
    decision: str
    approved: bool
    error: str | None = None


class ToolProxy:
    """Interposes governance checks on every tool invocation.

    Supports both synchronous and asynchronous tool execution, with optional
    timeouts and automatic call history tracking.

    Parameters
    ----------
    gateway : GovernanceGateway
        The :class:`~aegis.gateway.GovernanceGateway` through which all
        tool calls are governed.
    agent_id : str
        Identifier of the AI agent that owns this proxy.
    session_id : str
        Identifier of the current agent session.
    track_history : bool, optional
        Whether to track call history. Defaults to False.
    max_history_size : int, optional
        Maximum number of call records to keep. Defaults to 1000.
    """

    def __init__(
        self,
        gateway: GovernanceGateway,
        agent_id: str,
        session_id: str,
        track_history: bool = False,
        max_history_size: int = 1000,
    ) -> None:
        self._gateway = gateway
        self._agent_id = agent_id
        self._session_id = session_id
        self._track_history = track_history
        self._max_history_size = max_history_size
        # name -> (callable, governance_target)
        self._tools: dict[str, tuple[Callable[..., Any], str]] = {}
        # Call history
        self._call_history: list[CallRecord] = []

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
        name : str
            The logical name by which the tool is invoked.
        fn : callable
            The callable that implements the tool.
        target : str, optional
            The governance target string submitted in the AGP request.
            Defaults to *name* if not provided.
        """
        self._tools[name] = (fn, target or name)

    def unregister_tool(self, name: str) -> None:
        """Remove a tool registration (no-op if not registered).
        
        Parameters
        ----------
        name : str
            The name of the tool to unregister.
        """
        self._tools.pop(name, None)

    def registered_tools(self) -> list[str]:
        """Return the names of all registered tools.
        
        Returns
        -------
        list[str]
            List of registered tool names.
        """
        return list(self._tools.keys())

    # ------------------------------------------------------------------
    # Invocation
    # ------------------------------------------------------------------

    def call(self, tool_name: str, timeout: float | None = None, **kwargs: Any) -> Any:
        """Invoke *tool_name* subject to governance approval.

        The method constructs an :class:`~aegis.protocol.AGPRequest` with
        ``action.type = ActionType.TOOL_CALL``, submits it to the gateway,
        and only executes the tool if the decision is ``APPROVED``.

        Parameters
        ----------
        tool_name : str
            Name of the previously registered tool.
        timeout : float, optional
            Maximum execution time in seconds. If exceeded, raises TimeoutError.
            Default is None (no timeout).
        **kwargs
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
        TimeoutError
            If the execution exceeds the timeout.
        """
        start_time = time.perf_counter()
        
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
        
        # Record the decision in history
        if response.decision != Decision.APPROVED:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    False,
                    error=response.reason,
                )
            raise PermissionError(
                f"Tool call '{tool_name}' was {response.decision.value} by AEGIS: "
                f"{response.reason} (audit_id={response.audit_id})"
            )

        # Execute the tool
        try:
            result = fn(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    True,
                )
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    True,
                    error=str(e),
                )
            raise

    async def async_call(
        self,
        tool_name: str,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """Invoke *tool_name* asynchronously with governance approval.

        Like :meth:`call` but for async callables. The function is run in
        an executor to avoid blocking the event loop.

        Parameters
        ----------
        tool_name : str
            Name of the previously registered async tool.
        timeout : float, optional
            Maximum execution time in seconds. If exceeded, raises TimeoutError.
        **kwargs
            Keyword arguments forwarded to the tool callable.

        Returns
        -------
        Any
            The return value of the async tool callable.

        Raises
        ------
        ValueError
            If *tool_name* has not been registered.
        PermissionError
            If the governance decision is not ``APPROVED``.
        asyncio.TimeoutError
            If the execution exceeds the timeout.
        """
        start_time = time.perf_counter()
        
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
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    False,
                    error=response.reason,
                )
            raise PermissionError(
                f"Tool call '{tool_name}' was {response.decision.value} by AEGIS: "
                f"{response.reason} (audit_id={response.audit_id})"
            )

        # Execute the async tool
        try:
            loop = asyncio.get_event_loop()
            if asyncio.iscoroutinefunction(fn):
                result = await asyncio.wait_for(fn(**kwargs), timeout=timeout)
            else:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, fn, **kwargs),
                    timeout=timeout,
                )
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    True,
                )
            return result
        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    True,
                    error="execution timeout",
                )
            raise
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._track_history:
                self._record_call(
                    tool_name,
                    duration_ms,
                    response.decision.value,
                    True,
                    error=str(e),
                )
            raise

    # ------------------------------------------------------------------
    # Call history
    # ------------------------------------------------------------------

    def _record_call(
        self,
        tool_name: str,
        duration_ms: float,
        decision: str,
        approved: bool,
        error: str | None = None,
    ) -> None:
        """Record a tool call in the history.
        
        Parameters
        ----------
        tool_name : str
            The tool that was invoked.
        duration_ms : float
            Call duration in milliseconds.
        decision : str
            The governance decision string.
        approved : bool
            Whether the call was approved.
        error : str, optional
            Error message if the call failed.
        """
        record = CallRecord(
            tool_name=tool_name,
            timestamp=time.time(),
            duration_ms=duration_ms,
            decision=decision,
            approved=approved,
            error=error,
        )
        self._call_history.append(record)
        
        # Keep history bounded
        if len(self._call_history) > self._max_history_size:
            self._call_history.pop(0)

    def get_call_history(self) -> list[CallRecord]:
        """Get the call history.
        
        Returns
        -------
        list[CallRecord]
            List of recent tool call records (bounded by max_history_size).
        """
        return list(self._call_history)

    def clear_call_history(self) -> None:
        """Clear all call history records."""
        self._call_history.clear()
