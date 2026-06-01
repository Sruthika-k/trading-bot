"""
Binance API client wrapper for Futures Testnet.
"""

import logging
import json
from typing import Any, Dict, Optional
from binance.client import Client
from bot.exceptions import APIError

logger = logging.getLogger(__name__)

class BinanceClient:
    """
    Wrapper for the Binance API client focused on Futures Testnet.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initializes the BinanceClient.

        Args:
            api_key: Binance API Key.
            api_secret: Binance API Secret.
            testnet: Whether to use the Testnet (default: True).
        """
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            logger.info("Binance API client connected (Testnet: %s).", testnet)
        except Exception as e:
            logger.critical("Failed to connect to Binance API: %s", e)
            raise APIError(f"API Connection failed: {e}") from e

    def _log_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Helper to log API requests."""
        logger.debug("API REQUEST | Method: %s | Params: %s", method, params or {})

    def _log_response(self, method: str, response: Any) -> None:
        """Helper to log API responses."""
        logger.debug("API RESPONSE | Method: %s | Data: %s", method, json.dumps(response) if isinstance(response, dict) else response)

    def get_account_balance(self) -> Dict[str, Any]:
        """
        Fetches the account balance from Binance Futures.

        Returns:
            A dictionary containing balance information.

        Raises:
            APIError: If the API request fails.
        """
        method = "futures_account_balance"
        try:
            self._log_request(method)
            # In a real implementation: response = self.client.futures_account_balance()
            response = {"asset": "USDT", "balance": "1000.0"} # Placeholder
            self._log_response(method, response)
            return response
        except Exception as e:
            logger.error("API EXCEPTION | Method: %s | Error: %s", method, e)
            raise APIError(f"Balance fetch failed: {e}") from e

    def get_symbol_price(self, symbol: str) -> float:
        """
        Gets the current price for a given symbol.

        Args:
            symbol: The trading pair (e.g., 'BTCUSDT').

        Returns:
            The current price as a float.

        Raises:
            APIError: If the API request fails.
        """
        method = "get_symbol_ticker"
        params = {"symbol": symbol}
        try:
            self._log_request(method, params)
            # In a real implementation: response = self.client.get_symbol_ticker(symbol=symbol)
            response = {"symbol": symbol, "price": "50000.0"} # Placeholder
            self._log_response(method, response)
            return float(response["price"])
        except Exception as e:
            logger.error("API EXCEPTION | Method: %s | Params: %s | Error: %s", method, params, e)
            raise APIError(f"Price fetch failed for {symbol}") from e
