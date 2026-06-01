"""
Order management and execution logic.
"""

import logging
from typing import Any, Dict
from binance.exceptions import BinanceAPIException
from bot.client import BinanceClient
from bot.exceptions import OrderError
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
        Places a market order.

        Args:
            symbol: The trading pair.
            side: 'BUY' or 'SELL'.
            quantity: The amount to trade.

        Returns:
            The API response from Binance.

        Raises:
            OrderError: If validation or order placement fails.
        """
        # Prepare parameters for validation
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity
        }

        try:
            # Validate parameters before submission
            validate_order_params(params)
            
            logger.info("Placing %s market order for %s: %f", side, symbol, quantity)
            
            # Use get_client() to get the authenticated python-binance client
            futures_client = self.client.get_client()
            
            response = futures_client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            logger.info("Order placed successfully: %s", response.get('orderId'))
            return response
            
        except (BinanceAPIException, Exception) as e:
            # Re-wrap exceptions into OrderError
            error_msg = str(e.message) if hasattr(e, 'message') else str(e)
            logger.error("Order failed for %s: %s", symbol, error_msg)
            raise OrderError(f"Market order failed: {error_msg}") from e

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
