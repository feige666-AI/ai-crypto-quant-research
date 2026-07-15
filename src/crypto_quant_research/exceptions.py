"""Project-specific errors with user-facing meanings."""


class ResearchError(Exception):
    """Base class for expected project errors."""


class DataValidationError(ResearchError):
    """Raised when input market data is missing or invalid."""


class ConfigurationError(ResearchError):
    """Raised when strategy or backtest parameters are invalid."""


class OutputError(ResearchError):
    """Raised when a report or chart cannot be written."""
