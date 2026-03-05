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

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .exceptions import AEGISPolicyError
from .protocol import AGPRequest, Decision


class PolicyEffect(str, Enum):
    """The effect applied when a policy matches a request."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass
class PolicyCondition:
    """A single predicate that can be evaluated against an :class:`~aegis.protocol.AGPRequest`.

    Parameters
    ----------
    evaluate:
        A callable ``(AGPRequest) -> bool``.  Must be a pure function –
        side-effects are prohibited.
    description:
        Human-readable explanation used in audit output.
    """

    evaluate: Callable[[AGPRequest], bool]
    description: str


@dataclass
class Policy:
    """A governance rule.

    Parameters
    ----------
    id:
        Unique identifier.
    name:
        Short human-readable label.
    description:
        Longer description of the policy's intent.
    effect:
        Whether a match allows or denies the action.
    conditions:
        All conditions must match for the policy to apply.
    priority:
        Evaluation order; lower values are evaluated first.
        Deny policies are conventionally given lower (higher-priority)
        numbers than allow policies.
    enabled:
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
    """The outcome of evaluating a single policy against a request."""

    policy_id: str
    policy_name: str
    effect: str
    matched: bool


@dataclass(frozen=True)
class PolicyResult:
    """Aggregated result of evaluating all policies."""

    decision: Decision
    reason: str
    evaluations: list[PolicyEvaluation]


class PolicyEngine:
    """Evaluates an ordered set of :class:`Policy` rules deterministically.

    Usage::

        engine = PolicyEngine()
        engine.add_policy(Policy(...))
        result = engine.evaluate(request)
    """

    def __init__(self) -> None:
        self._policies: dict[str, Policy] = {}

    # ------------------------------------------------------------------
    # Policy management
    # ------------------------------------------------------------------

    def add_policy(self, policy: Policy) -> None:
        """Register a policy.

        Raises
        ------
        ValueError
            If a policy with the same ID already exists.
        """
        if policy.id in self._policies:
            raise ValueError(f"Policy '{policy.id}' is already registered.")
        self._policies[policy.id] = policy

    def remove_policy(self, policy_id: str) -> None:
        """Unregister a policy (no-op if not found)."""
        self._policies.pop(policy_id, None)

    def get_policy(self, policy_id: str) -> Policy | None:
        """Look up a policy by ID."""
        return self._policies.get(policy_id)

    def list_policies(self) -> list[Policy]:
        """Return all registered policies sorted by priority."""
        return sorted(self._policies.values(), key=lambda p: p.priority)

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
        3. On the first matching **deny** policy, return ``DENIED``.
        4. Record the first matching **allow** policy.
        5. After all policies: return ``APPROVED`` if an allow matched,
           otherwise return ``DENIED`` (default-deny).

        Raises
        ------
        AEGISPolicyError
            If a condition callable raises an unexpected exception.
        """
        evaluations: list[PolicyEvaluation] = []
        first_allow: Policy | None = None
        first_deny: Policy | None = None

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
                    first_deny = policy
                    break  # Deny at highest priority is immediately final
                elif first_allow is None and policy.effect == PolicyEffect.ALLOW:
                    first_allow = policy

        if first_deny is not None:
            return PolicyResult(
                decision=Decision.DENIED,
                reason=f"Denied by policy '{first_deny.name}'.",
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
