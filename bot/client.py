"""
Binance API client wrapper for Futures Testnet.
Encapsulates initialization, connection handling, and logging.
"""

import logging
import json
from typing import Any, Dict, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException, ConnectTimeout, ReadTimeout
from bot.exceptions import APIError, NetworkError

logger = logging.getLogger(__name__)

class BinanceClient:
    """
    Wrapper for the Binance API client focused on Futures Testnet.
    Provides an authenticated client and helper methods for common tasks.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initializes the BinanceClient.

        Args:
            api_key: Binance API Key.
            api_secret: Binance API Secret.
            testnet: Whether to use the Testnet (default: True).
            
        Raises:
            APIError: If connection to Binance fails.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
        self._client: Optional[Client] = None
        
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Private method to handle the actual connection and authentication.
        """
        try:
            logger.debug("Attempting to connect to Binance (Testnet: %s)...", self._testnet)
            self._client = Client(
                self._api_key, 
                self._api_secret, 
                testnet=self._testnet,
                requests_params={'timeout': 10}  # 10s timeout
            )
            
            # Explicitly set Futures Testnet URL if testnet is True
            # In python-binance, testnet=True in constructor mainly sets the Spot Testnet URL.
            if self._testnet:
                self._client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            
            # Verify connection with a simple ping
            self._client.ping()
            logger.info("Successfully connected to Binance API (Testnet: %s).", self._testnet)
            
        except (ConnectTimeout, ReadTimeout) as e:
            logger.error("Connection timeout during Binance initialization: %s", e)
            raise NetworkError(f"Connection to Binance timed out: {e}") from e
        except RequestException as e:
            logger.error("Network error during Binance initialization: %s", e)
            raise NetworkError(f"Could not connect to Binance: {e}") from e
        except BinanceAPIException as e:
            logger.error("Binance API error during initialization: %s (Code: %s)", e.message, e.status_code)
            raise APIError(f"Binance API initialization failed: {e.message}") from e
        except BinanceRequestException as e:
            logger.error("Binance Request error during initialization: %s", e)
            raise APIError(f"Invalid request to Binance: {e}") from e
        except Exception as e:
            logger.critical("Unexpected error during Binance client initialization: %s", e)
            raise APIError(f"Unexpected connection failure: {e}") from e

    def get_client(self) -> Client:
        """
        Returns the authenticated python-binance Client instance.
        
        Returns:
            Client: An authenticated Binance client instance.
            
        Raises:
            APIError: If the client is not initialized.
        """
        if not self._client:
            logger.warning("get_client called but client is None. Attempting re-initialization.")
            self._initialize_client()
            
        if not self._client:
            raise APIError("Binance client could not be initialized.")
            
        return self._client

    def _log_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Helper to log API requests at DEBUG level."""
        logger.debug("API REQUEST | Method: %s | Params: %s", method, params or {})

    def _log_response(self, method: str, response: Any) -> None:
        """Helper to log API responses at DEBUG level."""
        # Use json.dumps for pretty logging if it's a dict
        data = json.dumps(response) if isinstance(response, (dict, list)) else response
        logger.debug("API RESPONSE | Method: %s | Data: %s", method, data)

    def get_account_balance(self, asset: str = "USDT") -> Dict[str, Any]:
        """
        Fetches the account balance for a specific asset from Binance Futures.

        Args:
            asset: The asset to check balance for (default: 'USDT').

        Returns:
            A dictionary containing balance information.

        Raises:
            APIError: If the API request fails.
        """
        method = "futures_account_balance"
        try:
            client = self.get_client()
            self._log_request(method, {"asset": asset})
            
            balances = client.futures_account_balance()
            # Find the specific asset in the list of balances
            asset_balance = next((item for item in balances if item["asset"] == asset), {})
            
            self._log_response(method, asset_balance)
            return asset_balance
            
        except BinanceAPIException as e:
            logger.error("Binance API Error in %s: %s", method, e.message)
            raise APIError(f"Failed to fetch balance: {e.message}") from e
        except Exception as e:
            logger.error("Unexpected error in %s: %s", method, e)
            raise APIError(f"Unexpected failure during balance fetch: {e}") from e

    def get_symbol_price(self, symbol: str) -> float:
        """
        Gets the current mark price for a given futures symbol.

        Args:
            symbol: The trading pair (e.g., 'BTCUSDT').

        Returns:
            The current mark price as a float.

        Raises:
            APIError: If the API request fails.
        """
        method = "futures_symbol_ticker"
        params = {"symbol": symbol}
        try:
            client = self.get_client()
            self._log_request(method, params)
            
            response = client.futures_symbol_ticker(symbol=symbol)
            
            self._log_response(method, response)
            return float(response["price"])
            
        except BinanceAPIException as e:
            logger.error("Binance API Error in %s: %s", method, e.message)
            raise APIError(f"Failed to fetch price for {symbol}: {e.message}") from e
        except Exception as e:
            logger.error("Unexpected error in %s: %s", method, e)
            raise APIError(f"Unexpected failure during price fetch for {symbol}: {e}") from e
