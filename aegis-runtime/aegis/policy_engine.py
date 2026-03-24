"""Policy Engine.

Provides deterministic, priority-ordered policy evaluation as the
second layer of AEGIS enforcement.

Architecture
------------
* Each :class:`Policy` declares an *effect* (``allow`` or ``deny``) and
  a list of *conditions* (predicates over an :class:`~aegis.protocol.AGPRequest`).
* A policy *matches* a request when **all** of its conditions evaluate to
  ``True``.
* Policies are evaluated in ascending *priority* order (lower number =
  evaluated first).
* The first matching **deny** policy immediately produces a
  ``DENIED`` decision.
* If no deny policy matches, the first matching **allow** policy produces
  an ``APPROVED`` decision.
* If neither a deny nor an allow policy matches, the engine returns
  ``DENIED`` (default-deny posture).

This ensures that governance decisions are fully deterministic: the same
request against the same policy set always yields the same outcome.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .exceptions import AEGISPolicyError
from .protocol import AGPRequest, Decision


class PolicyEffect(str, Enum):
    """The effect applied when a policy matches a request."""

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    REQUIRE_CONFIRMATION = "require_confirmation"


@dataclass
class PolicyCondition:
    """A single predicate that can be evaluated against an :class:`~aegis.protocol.AGPRequest`.

    Parameters
    ----------
    evaluate : callable
        A callable ``(AGPRequest) -> bool``.  Must be a pure function –
        side-effects are prohibited.
    description : str
        Human-readable explanation used in audit output.
    """

    evaluate: Callable[[AGPRequest], bool]
    description: str


@dataclass
class Policy:
    """A governance rule.

    Parameters
    ----------
    id : str
        Unique identifier.
    name : str
        Short human-readable label.
    description : str
        Longer description of the policy's intent.
    effect : PolicyEffect
        Whether a match allows or denies the action.
    conditions : list[PolicyCondition]
        All conditions must match for the policy to apply.
    priority : int, optional
        Evaluation order; lower values are evaluated first.
        Deny policies are conventionally given lower (higher-priority)
        numbers than allow policies.
    enabled : bool, optional
        Disabled policies are skipped during evaluation.
    """

    id: str
    name: str
    description: str
    effect: PolicyEffect
    conditions: list[PolicyCondition]
    priority: int = 200
    enabled: bool = True


@dataclass(frozen=True)
class PolicyEvaluation:
    """The outcome of evaluating a single policy against a request.
    
    Parameters
    ----------
    policy_id : str
        The policy ID evaluated.
    policy_name : str
        The policy name.
    effect : str
        The effect ("allow" or "deny").
    matched : bool
        Whether the policy's conditions matched the request.
    """

    policy_id: str
    policy_name: str
    effect: str
    matched: bool


@dataclass(frozen=True)
class PolicyResult:
    """Aggregated result of evaluating all policies.
    
    Parameters
    ----------
    decision : Decision
        The final governance decision.
    reason : str
        Human-readable explanation of the decision.
    evaluations : list[PolicyEvaluation]
        Per-policy evaluation trace.
    """

    decision: Decision
    reason: str
    evaluations: list[PolicyEvaluation]


class PolicyEngine:
    """Evaluates an ordered set of :class:`Policy` rules deterministically.

    All operations are thread-safe via internal locking.

    Usage::

        engine = PolicyEngine()
        engine.add_policy(Policy(...))
        result = engine.evaluate(request)
    """

    def __init__(self) -> None:
        self._policies: dict[str, Policy] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Policy management
    # ------------------------------------------------------------------

    def add_policy(self, policy: Policy) -> None:
        """Register a policy.

        Parameters
        ----------
        policy : Policy
            The policy to register.

        Raises
        ------
        ValueError
            If a policy with the same ID already exists.
        AEGISPolicyError
            If the policy is invalid.
        """
        self.validate_policy(policy)
        with self._lock:
            if policy.id in self._policies:
                raise ValueError(f"Policy '{policy.id}' is already registered.")
            self._policies[policy.id] = policy

    def remove_policy(self, policy_id: str) -> None:
        """Unregister a policy (no-op if not found).
        
        Parameters
        ----------
        policy_id : str
            The policy ID to remove.
        """
        with self._lock:
            self._policies.pop(policy_id, None)

    def get_policy(self, policy_id: str) -> Policy | None:
        """Look up a policy by ID.
        
        Parameters
        ----------
        policy_id : str
            The policy ID to retrieve.
            
        Returns
        -------
        Policy or None
            The policy if found, None otherwise.
        """
        with self._lock:
            return self._policies.get(policy_id)

    def list_policies(self) -> list[Policy]:
        """Return all registered policies sorted by priority.
        
        Returns
        -------
        list[Policy]
            All policies sorted by priority (lower numbers first).
        """
        with self._lock:
            return sorted(self._policies.values(), key=lambda p: p.priority)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_policy(self, policy: Policy) -> None:
        """Validate policy structure and integrity.
        
        Checks:
        - Policy ID is non-empty
        - Policy name is non-empty
        - Effect is valid (ALLOW, DENY, ESCALATE, or REQUIRE_CONFIRMATION)
        - All conditions have callable evaluate functions
        
        Parameters
        ----------
        policy : Policy
            The policy to validate.
            
        Raises
        ------
        AEGISPolicyError
            If the policy is invalid.
        """
        if not policy.id or not policy.id.strip():
            raise AEGISPolicyError(
                "Policy.id must not be empty",
                error_code="EMPTY_POLICY_ID"
            )
        
        if not policy.name or not policy.name.strip():
            raise AEGISPolicyError(
                "Policy.name must not be empty",
                error_code="EMPTY_POLICY_NAME"
            )
        
        if policy.effect not in (PolicyEffect.ALLOW, PolicyEffect.DENY, PolicyEffect.ESCALATE, PolicyEffect.REQUIRE_CONFIRMATION):
            raise AEGISPolicyError(
                f"Policy.effect must be ALLOW, DENY, ESCALATE, or REQUIRE_CONFIRMATION, got {policy.effect}",
                error_code="INVALID_POLICY_EFFECT"
            )
        
        if not isinstance(policy.conditions, list):
            raise AEGISPolicyError(
                f"Policy.conditions must be a list, got {type(policy.conditions).__name__}",
                error_code="INVALID_CONDITIONS_TYPE"
            )
        
        for i, condition in enumerate(policy.conditions):
            if not callable(condition.evaluate):
                raise AEGISPolicyError(
                    f"Policy condition {i}: evaluate is not callable",
                    error_code="NONCALLABLE_CONDITION"
                )
            if not condition.description or not condition.description.strip():
                raise AEGISPolicyError(
                    f"Policy condition {i}: description must not be empty",
                    error_code="EMPTY_CONDITION_DESCRIPTION"
                )

    def find_policies_by_effect(self, effect: PolicyEffect) -> list[Policy]:
        """Find all policies with a specific effect.
        
        Parameters
        ----------
        effect : PolicyEffect
            The effect to filter by (ALLOW or DENY).
            
        Returns
        -------
        list[Policy]
            All matching policies sorted by priority.
        """
        with self._lock:
            matching = [p for p in self._policies.values() if p.effect == effect]
        return sorted(matching, key=lambda p: p.priority)

    def find_matching_policies(self, request: AGPRequest) -> list[Policy]:
        """Find all enabled policies that would match the given request.
        
        Parameters
        ----------
        request : AGPRequest
            The request to test against all policies.
            
        Returns
        -------
        list[Policy]
            All policies whose conditions are satisfied by the request,
            sorted by priority.
        """
        matching = []
        with self._lock:
            for policy in self._policies.values():
                if not policy.enabled:
                    continue
                try:
                    if all(cond.evaluate(request) for cond in policy.conditions):
                        matching.append(policy)
                except Exception:
                    # Silently skip policies with errors
                    pass
        return sorted(matching, key=lambda p: p.priority)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, request: AGPRequest) -> PolicyResult:
        """Evaluate all enabled policies against *request*.

        Returns a :class:`PolicyResult` with the final :class:`~aegis.protocol.Decision`,
        a human-readable reason, and the per-policy evaluation trace.

        The algorithm is deterministic:

        1. Sort enabled policies by ascending *priority*.
        2. Evaluate each policy's conditions against the request.
        3. On the first matching **deny** policy, return ``DENIED`` immediately.
        4. Record the first matching **escalate**, **require_confirmation**,
           or **allow** policy.
        5. After all policies: return the most restrictive matched effect
           (deny > escalate > require_confirmation > allow),
           or ``DENIED`` if nothing matched (default-deny).

        Parameters
        ----------
        request : AGPRequest
            The request to evaluate.

        Returns
        -------
        PolicyResult
            The evaluation result with decision, reason, and trace.

        Raises
        ------
        AEGISPolicyError
            If a condition callable raises an unexpected exception.
        """
        evaluations: list[PolicyEvaluation] = []
        first_allow: Policy | None = None
        first_escalate: Policy | None = None
        first_require_confirmation: Policy | None = None

        with self._lock:
            sorted_policies = sorted(
                (p for p in self._policies.values() if p.enabled),
                key=lambda p: p.priority,
            )

        for policy in sorted_policies:
            try:
                matched = all(cond.evaluate(request) for cond in policy.conditions)
            except Exception as exc:
                raise AEGISPolicyError(
                    f"Policy '{policy.id}' condition raised an error: {exc}"
                ) from exc

            evaluations.append(
                PolicyEvaluation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    effect=policy.effect.value,
                    matched=matched,
                )
            )

            if matched:
                if policy.effect == PolicyEffect.DENY:
                    # Deny is immediately final — highest precedence
                    return PolicyResult(
                        decision=Decision.DENIED,
                        reason=f"Denied by policy '{policy.name}'.",
                        evaluations=evaluations,
                    )
                elif policy.effect == PolicyEffect.ESCALATE and first_escalate is None:
                    first_escalate = policy
                elif policy.effect == PolicyEffect.REQUIRE_CONFIRMATION and first_require_confirmation is None:
                    first_require_confirmation = policy
                elif policy.effect == PolicyEffect.ALLOW and first_allow is None:
                    first_allow = policy

        # Precedence: deny (handled above) > escalate > require_confirmation > allow
        if first_escalate is not None:
            return PolicyResult(
                decision=Decision.ESCALATE,
                reason=f"Escalation required by policy '{first_escalate.name}'.",
                evaluations=evaluations,
            )

        if first_require_confirmation is not None:
            return PolicyResult(
                decision=Decision.REQUIRE_CONFIRMATION,
                reason=f"Human confirmation required by policy '{first_require_confirmation.name}'.",
                evaluations=evaluations,
            )

        if first_allow is not None:
            return PolicyResult(
                decision=Decision.APPROVED,
                reason=f"Approved by policy '{first_allow.name}'.",
                evaluations=evaluations,
            )

        return PolicyResult(
            decision=Decision.DENIED,
            reason="No matching allow policy found (default-deny).",
            evaluations=evaluations,
        )
