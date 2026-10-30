class AIError(Exception):
    """Base exception for Kaushal Radar AI."""

class ProviderError(AIError):
    """Provider unavailable or failed."""

class ValidationError(AIError):
    """Invalid AI input or output."""

class InsufficientEvidence(AIError):
    """Evidence is insufficient for a reliable answer."""
