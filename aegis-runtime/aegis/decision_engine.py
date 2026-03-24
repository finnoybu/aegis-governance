"""Decision Engine.

The Decision Engine is the authoritative evaluator of every AGP request.
It orchestrates the two-stage governance pipeline:

1. **Capability check** – Does the agent hold a capability that covers
   this action type and target?  If not, deny immediately.
2. **Policy evaluation** – Do the configured policies allow the action?

Every decision, regardless of outcome, is committed to the :class:`~aegis.audit.AuditSystem`
before the :class:`~aegis.protocol.AGPResponse` is returned.  This ensures
full auditability even for denied requests.

The Decision Engine also provides telemetry hooks and metrics for
instrumentation and monitoring of governance decisions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .audit import AuditSystem
from .capability_registry import CapabilityRegistry
from .policy_engine import PolicyEngine
from .protocol import AGPRequest, AGPResponse, Decision


@dataclass
class DecisionMetrics:
    """Aggregated metrics about governance decisions.
    
    Parameters
    ----------
    total_decisions : int
        Total number of decisions evaluated.
    approved_count : int
        Number of decisions that were APPROVED.
    denied_count : int
        Number of decisions that were DENIED.
    deferred_count : int
        Number of decisions that were ESCALATE.
    capability_denials : int
        Number of decisions denied in stage 1 (capability check).
    policy_denials : int
        Number of decisions denied in stage 2 (policy evaluation).
    total_latency_ms : float
        Cumulative latency of all decisions in milliseconds.
    avg_latency_ms : float
        Average decision latency in milliseconds.
    """
    
    total_decisions: int = 0
    approved_count: int = 0
    denied_count: int = 0
    deferred_count: int = 0
    capability_denials: int = 0
    policy_denials: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0


class DecisionEngine:
    """Evaluates :class:`~aegis.protocol.AGPRequest` objects and returns
    :class:`~aegis.protocol.AGPResponse` objects.

    Provides comprehensive telemetry hooks and metrics collection for
    monitoring and instrumentation of governance decisions.

    Parameters
    ----------
    capability_registry : CapabilityRegistry
        Registry used for the capability check (stage 1).
    policy_engine : PolicyEngine
        Engine used for policy evaluation (stage 2).
    audit_system : AuditSystem
        Audit system where every decision is recorded.
    """

    def __init__(
        self,
        capability_registry: CapabilityRegistry,
        policy_engine: PolicyEngine,
        audit_system: AuditSystem,
    ) -> None:
        self._capabilities = capability_registry
        self._policies = policy_engine
        self._audit = audit_system
        
        # Metrics collection
        self._metrics = DecisionMetrics()

    def evaluate(self, request: AGPRequest) -> AGPResponse:
        """Run the full governance pipeline for *request*.

        Returns an :class:`~aegis.protocol.AGPResponse` whose
        :attr:`~aegis.protocol.AGPResponse.decision` field is the
        authoritative governance decision.

        The method is intentionally synchronous and free of side-effects
        beyond writing to the audit log and recording metrics, making it
        straightforward to test deterministically.
        
        Parameters
        ----------
        request : AGPRequest
            The governance request to evaluate.
            
        Returns
        -------
        AGPResponse
            The governance decision response.
        """
        start_time = time.perf_counter()
        
        action_type: str = (
            request.action.type.value
            if hasattr(request.action.type, "value")
            else str(request.action.type)
        )

        # ------------------------------------------------------------------
        # Stage 1: Capability check
        # ------------------------------------------------------------------
        has_capability = self._capabilities.has_capability_for_action(
            request.agent_id,
            action_type,
            request.action.target,
        )

        if not has_capability:
            decision = Decision.DENIED
            reason = (
                f"Agent '{request.agent_id}' lacks a capability covering "
                f"action '{action_type}' on target '{request.action.target}'."
            )
            policy_evaluations: list[dict] = []
            # Telemetry: capability denial
            self._metrics.capability_denials += 1
        else:
            # --------------------------------------------------------------
            # Stage 2: Policy evaluation
            # --------------------------------------------------------------
            policy_result = self._policies.evaluate(request)
            decision = policy_result.decision
            reason = policy_result.reason
            policy_evaluations = [
                {
                    "policy_id": ev.policy_id,
                    "policy_name": ev.policy_name,
                    "effect": ev.effect,
                    "matched": ev.matched,
                }
                for ev in policy_result.evaluations
            ]
            
            # Telemetry: policy-stage denial
            if decision == Decision.DENIED:
                self._metrics.policy_denials += 1

        # ------------------------------------------------------------------
        # Audit (always, regardless of decision)
        # ------------------------------------------------------------------
        audit_id = self._audit.record(
            request_id=request.request_id,
            agent_id=request.agent_id,
            action_type=action_type,
            action_target=request.action.target,
            action_parameters=request.action.parameters,
            decision=decision.value,
            reason=reason,
            policy_evaluations=policy_evaluations,
            session_id=request.context.session_id,
        )

        # ------------------------------------------------------------------
        # Telemetry collection
        # ------------------------------------------------------------------
        latency_ms = (time.perf_counter() - start_time) * 1000
        self._record_decision_metrics(decision, latency_ms)

        return AGPResponse(
            request_id=request.request_id,
            decision=decision,
            reason=reason,
            audit_id=audit_id,
        )

    # ------------------------------------------------------------------
    # Metrics and telemetry
    # ------------------------------------------------------------------

    def _record_decision_metrics(self, decision: Decision, latency_ms: float) -> None:
        """Record metrics for a decision.
        
        Parameters
        ----------
        decision : Decision
            The decision outcome.
        latency_ms : float
            The decision latency in milliseconds.
        """
        self._metrics.total_decisions += 1
        self._metrics.total_latency_ms += latency_ms
        self._metrics.avg_latency_ms = (
            self._metrics.total_latency_ms / self._metrics.total_decisions
        )
        
        if decision == Decision.APPROVED:
            self._metrics.approved_count += 1
        elif decision == Decision.DENIED:
            self._metrics.denied_count += 1
        elif decision == Decision.ESCALATE:
            self._metrics.deferred_count += 1

    def get_metrics(self) -> DecisionMetrics:
        """Get current decision metrics.
        
        Returns
        -------
        DecisionMetrics
            Current metrics snapshot.
        """
        return self._metrics

    def reset_metrics(self) -> None:
        """Reset metrics counters to zero.
        
        Useful for periodic metric window resets.
        """
        self._metrics = DecisionMetrics()
