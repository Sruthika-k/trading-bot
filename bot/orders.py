"""
Order management and execution logic.
"""

import logging
import json
from typing import Any, Dict, Optional
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException, ConnectTimeout, ReadTimeout
from bot.client import BinanceClient
from bot.exceptions import OrderError, ValidationError, NetworkError
from bot.validators import validate_order_params

logger = logging.getLogger(__name__)

def format_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely extracts and formats key fields from a Binance order response.

    Args:
        response: Raw dictionary response from the Binance API.

    Returns:
        Dict[str, Any]: A structured dictionary containing:
            - order_id (int/str): The unique ID of the order.
            - status (str): Current status of the order (e.g., 'FILLED', 'NEW').
            - executed_qty (float): The quantity that has been executed.
            - avg_price (float): The average price of execution.
    """
    return {
        "order_id": response.get("orderId", "N/A"),
        "status": response.get("status", "UNKNOWN"),
        "executed_qty": float(response.get("executedQty", response.get("origQty", 0))),
        "avg_price": float(response.get("avgPrice", response.get("price", 0))),
        "symbol": response.get("symbol", "N/A"),
        "side": response.get("side", "N/A"),
        "type": response.get("type", "N/A")
    }

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

    def place_order(
        self, 
        symbol: str, 
        side: str, 
        order_type: str, 
        quantity: float, 
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Unified service function to place Market or Limit orders on Binance Futures.

        Args:
            symbol: The trading pair (e.g., 'BTCUSDT').
            side: 'BUY' or 'SELL'.
            order_type: 'MARKET' or 'LIMIT'.
            quantity: The amount to trade.
            price: The limit price (required for LIMIT orders).

        Returns:
            Dict[str, Any]: The structured API response from Binance.

        Raises:
            OrderError: If the order placement fails due to API or network issues.
            ValidationError: If the input parameters are invalid.
        """
        # 1. Prepare parameters
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }

        # Add price and GTC timeInForce for LIMIT orders
        if order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"

        # 2. Validate inputs
        try:
            validate_order_params(params)
        except ValidationError as e:
            logger.error("Validation failed for %s order: %s", order_type, e)
            raise

        # 3. Log request
        log_msg = f"{order_type} ORDER REQUEST | {side} {symbol} | Qty: {quantity}"
        if price:
            log_msg += f" | Price: {price} | TIF: GTC"
        logger.info(log_msg)
        logger.debug("Order Params: %s", params)

        try:
            # 4. Submit Binance Futures order
            futures_client = self.client.get_client()
            response = futures_client.futures_create_order(**params)

            # 5. Log response and return structured object
            formatted_response = format_order_response(response)
            logger.info("%s ORDER SUCCESS | Symbol: %s | OrderID: %s | Status: %s", 
                        order_type, formatted_response.get('symbol'), 
                        formatted_response.get('order_id'), 
                        formatted_response.get('status'))
            logger.debug("Full Response: %s", json.dumps(response))
            
            return formatted_response

        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.status_code})"
            logger.error("%s ORDER FAILED | %s", order_type, error_msg)
            raise OrderError(error_msg) from e

        except BinanceRequestException as e:
            error_msg = f"Binance Request Error: {str(e)}"
            logger.error("%s ORDER FAILED | %s", order_type, error_msg)
            raise OrderError(error_msg) from e

        except (ConnectTimeout, ReadTimeout) as e:
            error_msg = f"Network Timeout: Connection to Binance timed out. {str(e)}"
            logger.error("%s ORDER FAILED | %s", order_type, error_msg)
            raise NetworkError(error_msg) from e

        except RequestException as e:
            error_msg = f"Network Error: Could not connect to Binance. {str(e)}"
            logger.error("%s ORDER FAILED | %s", order_type, error_msg)
            raise NetworkError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            logger.error("%s ORDER FAILED | %s", order_type, error_msg)
            raise OrderError(error_msg) from e

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Legacy helper for market orders."""
        return self.place_order(symbol, side, "MARKET", quantity)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """Legacy helper for limit orders."""
        return self.place_order(symbol, side, "LIMIT", quantity, price)

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
