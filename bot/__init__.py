"""
Binance Futures Testnet Trading Bot package.
"""

from bot.exceptions import TradingBotError, APIError, ValidationError, NetworkError, ConfigurationError
from bot.config import AppConfig, get_config
from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import OrderManager

__version__ = "0.1.0"
__all__ = [
    "TradingBotError",
    "APIError",
    "ValidationError",
    "NetworkError",
    "ConfigurationError",
    "AppConfig",
    "get_config",
    "setup_logging",
    "BinanceClient",
    "OrderManager",
]
