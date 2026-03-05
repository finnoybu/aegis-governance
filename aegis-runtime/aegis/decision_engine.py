"""Decision Engine.

The Decision Engine is the authoritative evaluator of every AGP request.
It orchestrates the two-stage governance pipeline:

1. **Capability check** – Does the agent hold a capability that covers
   this action type and target?  If not, deny immediately.
2. **Policy evaluation** – Do the configured policies allow the action?

Every decision, regardless of outcome, is committed to the :class:`~aegis.audit.AuditSystem`
before the :class:`~aegis.protocol.AGPResponse` is returned.  This ensures
full auditability even for denied requests.
"""

from __future__ import annotations

from .audit import AuditSystem
from .capability_registry import CapabilityRegistry
from .policy_engine import PolicyEngine
from .protocol import AGPRequest, AGPResponse, Decision


class DecisionEngine:
    """Evaluates :class:`~aegis.protocol.AGPRequest` objects and returns
    :class:`~aegis.protocol.AGPResponse` objects.

    Parameters
    ----------
    capability_registry:
        Registry used for the capability check (stage 1).
    policy_engine:
        Engine used for policy evaluation (stage 2).
    audit_system:
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

    def evaluate(self, request: AGPRequest) -> AGPResponse:
        """Run the full governance pipeline for *request*.

        Returns an :class:`~aegis.protocol.AGPResponse` whose
        :attr:`~aegis.protocol.AGPResponse.decision` field is the
        authoritative governance decision.

        The method is intentionally synchronous and free of side-effects
        beyond writing to the audit log, making it straightforward to
        test deterministically.
        """
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

        return AGPResponse(
            request_id=request.request_id,
            decision=decision,
            reason=reason,
            audit_id=audit_id,
        )
