"""
Order management and execution logic.
"""

import logging
import json
from typing import Any, Dict
from binance.exceptions import BinanceAPIException
from requests.exceptions import RequestException
from bot.client import BinanceClient
from bot.exceptions import OrderError, ValidationError
from bot.validators import validate_order_params

logger = logging.getLogger(__name__)

class OrderManager:
    """
    Handles placing and managing orders on Binance Futures.
    Uses the authenticated client from BinanceClient and validates inputs.
    """

    def __init__(self, client: BinanceClient):
        """
        Initializes the OrderManager.

        Args:
            client: An instance of BinanceClient.
        """
        self.client = client

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Places a market order on Binance Futures.

        Args:
            symbol: The trading pair (e.g., 'BTCUSDT').
            side: 'BUY' or 'SELL'.
            quantity: The amount to trade.

        Returns:
            Dict[str, Any]: The structured API response from Binance.

        Raises:
            OrderError: If the order placement fails due to API or network issues.
            ValidationError: If the input parameters are invalid.
        """
        # 1. Validate inputs
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": "MARKET",
            "quantity": quantity
        }

        try:
            validate_order_params(params)
        except ValidationError as e:
            logger.error("Validation failed for market order: %s", e)
            raise

        # 2. Log request
        logger.info("MARKET ORDER REQUEST | %s %s | Quantity: %f", side.upper(), symbol.upper(), quantity)
        logger.debug("Order Params: %s", params)

        try:
            # 3. Submit Binance Futures MARKET order
            futures_client = self.client.get_client()
            response = futures_client.futures_create_order(**params)

            # 4. Log response and return structured object
            logger.info("MARKET ORDER SUCCESS | Symbol: %s | OrderID: %s | Status: %s", 
                        response.get('symbol'), response.get('orderId'), response.get('status'))
            logger.debug("Full Response: %s", json.dumps(response))
            
            return response

        except BinanceAPIException as e:
            # 5. Handle BinanceAPIException
            error_msg = f"Binance API Error: {e.message} (Code: {e.status_code})"
            logger.error("MARKET ORDER FAILED | %s", error_msg)
            raise OrderError(error_msg) from e

        except RequestException as e:
            # 6. Handle network errors
            error_msg = f"Network Error: Could not connect to Binance. {str(e)}"
            logger.error("MARKET ORDER FAILED | %s", error_msg)
            raise OrderError(error_msg) from e

        except Exception as e:
            # 7. Handle unexpected exceptions
            error_msg = f"Unexpected Error: {str(e)}"
            logger.error("MARKET ORDER FAILED | %s", error_msg)
            raise OrderError(error_msg) from e

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Cancels an existing order.

        Args:
            symbol: The trading pair.
            order_id: The ID of the order to cancel.

        Returns:
            The API response from Binance.

        Raises:
            OrderError: If the cancellation fails.
        """
        try:
            logger.info("Cancelling order %s for %s", order_id, symbol)
            
            futures_client = self.client.get_client()
            
            response = futures_client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            
            logger.info("Order %s cancelled successfully", order_id)
            return response
            
        except BinanceAPIException as e:
            logger.error("Binance API error cancelling order %s: %s", order_id, e.message)
            raise OrderError(f"Order cancellation failed: {e.message}") from e
        except Exception as e:
            logger.error("Unexpected error cancelling order %s: %s", order_id, e)
            raise OrderError(f"Cancellation failed: {e}") from e
