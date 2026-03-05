"""Audit System.

Provides an immutable, append-only record of every governance decision
made by AEGIS.  Records are stored in a SQLite database and can be
queried for compliance reporting and forensic review.

Design principles
-----------------
* **Immutable** – records are never updated or deleted.
* **Complete** – every AGP request/response pair is recorded regardless
  of the decision outcome.
* **Queryable** – records can be retrieved by audit ID or agent ID.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .exceptions import AEGISAuditError


@dataclass(frozen=True)
class AuditRecord:
    """An immutable record of a single governance decision."""

    id: str
    request_id: str
    agent_id: str
    action_type: str
    action_target: str
    action_parameters: dict[str, Any]
    decision: str
    reason: str
    policy_evaluations: list[dict[str, Any]]
    session_id: str
    timestamp: str


class AuditSystem:
    """SQLite-backed, append-only governance audit trail.

    Parameters
    ----------
    db_path:
        File path for the SQLite database.  Defaults to ``":memory:"``
        which is useful for testing.
    """

    _CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS audit_records (
            id                 TEXT PRIMARY KEY,
            request_id         TEXT NOT NULL,
            agent_id           TEXT NOT NULL,
            action_type        TEXT NOT NULL,
            action_target      TEXT NOT NULL,
            action_parameters  TEXT NOT NULL,
            decision           TEXT NOT NULL,
            reason             TEXT NOT NULL,
            policy_evaluations TEXT NOT NULL,
            session_id         TEXT NOT NULL,
            timestamp          TEXT NOT NULL
        )
    """

    _COLUMNS = (
        "id",
        "request_id",
        "agent_id",
        "action_type",
        "action_target",
        "action_parameters",
        "decision",
        "reason",
        "policy_evaluations",
        "session_id",
        "timestamp",
    )

    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute(self._CREATE_TABLE)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record(
        self,
        *,
        request_id: str,
        agent_id: str,
        action_type: str,
        action_target: str,
        action_parameters: dict[str, Any],
        decision: str,
        reason: str,
        policy_evaluations: list[dict[str, Any]],
        session_id: str,
    ) -> str:
        """Append a governance decision to the audit trail.

        Returns
        -------
        str
            The newly generated audit record ID.

        Raises
        ------
        AEGISAuditError
            If the record cannot be persisted.
        """
        audit_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            self._conn.execute(
                f"INSERT INTO audit_records ({', '.join(self._COLUMNS)}) "  # noqa: S608
                f"VALUES ({', '.join(['?'] * len(self._COLUMNS))})",
                (
                    audit_id,
                    request_id,
                    agent_id,
                    action_type,
                    action_target,
                    json.dumps(action_parameters),
                    decision,
                    reason,
                    json.dumps(policy_evaluations),
                    session_id,
                    timestamp,
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise AEGISAuditError(f"Failed to persist audit record: {exc}") from exc

        return audit_id

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_record(self, audit_id: str) -> AuditRecord | None:
        """Retrieve a single audit record by its ID."""
        cursor = self._conn.execute(
            "SELECT * FROM audit_records WHERE id = ?", (audit_id,)
        )
        row = cursor.fetchone()
        return self._row_to_record(row) if row else None

    def get_agent_history(
        self, agent_id: str, *, limit: int = 100
    ) -> list[AuditRecord]:
        """Return the most recent *limit* audit records for *agent_id*."""
        cursor = self._conn.execute(
            "SELECT * FROM audit_records "
            "WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?",
            (agent_id, limit),
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_session_history(self, session_id: str) -> list[AuditRecord]:
        """Return all audit records for a given session."""
        cursor = self._conn.execute(
            "SELECT * FROM audit_records "
            "WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _row_to_record(self, row: tuple) -> AuditRecord:
        data = dict(zip(self._COLUMNS, row))
        data["action_parameters"] = json.loads(data["action_parameters"])
        data["policy_evaluations"] = json.loads(data["policy_evaluations"])
        return AuditRecord(**data)
