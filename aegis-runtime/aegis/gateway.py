"""Governance Gateway.

The Governance Gateway is the single, validated entry point through
which AI agents submit :class:`~aegis.protocol.AGPRequest` objects for
governance review.

Responsibilities
----------------
* **Schema validation** – rejects structurally or semantically invalid
  requests before they reach the Decision Engine.
* **Routing** – forwards valid requests to the :class:`~aegis.decision_engine.DecisionEngine`.

All interaction with AEGIS from external code should go through this
class rather than calling the Decision Engine directly.
"""

from __future__ import annotations

from .decision_engine import DecisionEngine
from .exceptions import AEGISValidationError
from .protocol import AGPRequest, AGPResponse


class GovernanceGateway:
    """Validates and routes AGP requests to the Decision Engine.

    Parameters
    ----------
    decision_engine:
        The :class:`~aegis.decision_engine.DecisionEngine` instance that
        will evaluate governance decisions.
    """

    def __init__(self, decision_engine: DecisionEngine) -> None:
        self._engine = decision_engine

    def submit(self, request: AGPRequest) -> AGPResponse:
        """Submit a governance request.

        Parameters
        ----------
        request:
            The :class:`~aegis.protocol.AGPRequest` to evaluate.

        Returns
        -------
        AGPResponse
            The governance decision.

        Raises
        ------
        AEGISValidationError
            If the request is structurally invalid.
        """
        self._validate(request)
        return self._engine.evaluate(request)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self, request: AGPRequest) -> None:
        """Raise :class:`~aegis.exceptions.AEGISValidationError` for invalid requests."""
        if not request.agent_id or not request.agent_id.strip():
            raise AEGISValidationError("AGPRequest.agent_id must not be empty.")

        if not request.action.target or not request.action.target.strip():
            raise AEGISValidationError("AGPRequest.action.target must not be empty.")

        if not request.context.session_id or not request.context.session_id.strip():
            raise AEGISValidationError("AGPRequest.context.session_id must not be empty.")
