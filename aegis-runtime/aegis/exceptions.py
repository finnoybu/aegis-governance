"""Custom exceptions for the AEGIS governance framework."""


class AEGISError(Exception):
    """Base exception for all AEGIS errors."""


class AEGISValidationError(AEGISError):
    """Raised when an AGP request fails schema or semantic validation."""


class AEGISCapabilityError(AEGISError):
    """Raised when an agent lacks the capability required for an action."""


class AEGISPolicyError(AEGISError):
    """Raised when policy evaluation encounters an unexpected error."""


class AEGISAuditError(AEGISError):
    """Raised when the audit system is unable to record a decision."""
