"""
Custom exceptions for the trading bot.
"""

class TradingBotError(Exception):
    """Base exception for all trading bot errors."""
    pass

class APIError(TradingBotError):
    """Raised when there is an issue with the Binance API."""
    pass

class ValidationError(TradingBotError):
    """Raised when data validation fails."""
    pass

class ConfigurationError(TradingBotError):
    """Raised when there is a configuration error."""
    pass

class MissingCredentialError(ConfigurationError):
    """Raised when a required API credential is missing."""
    pass

class OrderError(TradingBotError):
    """Raised when an order cannot be placed or managed."""
    pass
