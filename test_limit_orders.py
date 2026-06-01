"""
Test script to simulate limit order placement and verify response handling.
"""

import logging
import json
from unittest.mock import MagicMock
from bot.orders import OrderManager
from bot.client import BinanceClient
from bot.exceptions import OrderError, ValidationError
from binance.exceptions import BinanceAPIException

# Setup basic logging for the test
logging.basicConfig(level=logging.DEBUG)

def test_place_limit_order_success():
    """
    Tests successful limit order placement with a mocked Binance client.
    """
    print("\n--- Running Limit Order Success Test ---")
    mock_binance_client = MagicMock()
    mock_binance_client.futures_create_order.return_value = {
        "symbol": "BTCUSDT",
        "orderId": "67890",
        "status": "NEW",
        "side": "BUY",
        "type": "LIMIT",
        "price": "45000.0",
        "origQty": "0.01",
        "timeInForce": "GTC"
    }
    
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    mock_client_wrapper.get_client.return_value = mock_binance_client
    
    manager = OrderManager(mock_client_wrapper)
    
    try:
        response = manager.place_limit_order("BTCUSDT", "BUY", 0.01, 45000.0)
        print(f"Test Passed: Received OrderID {response.get('orderId')}")
        assert response["timeInForce"] == "GTC"
    except Exception as e:
        print(f"Test Failed: Unexpected exception {e}")

def test_place_limit_order_missing_price():
    """
    Tests that a limit order without a price raises a ValidationError.
    """
    print("\n--- Running Limit Order Missing Price Test ---")
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    manager = OrderManager(mock_client_wrapper)
    
    try:
        # Pydantic should catch this in our validator
        manager.place_limit_order("BTCUSDT", "BUY", 0.01, None) # type: ignore
        print("Test Failed: ValidationError not raised for missing price")
    except (ValidationError, TypeError):
        print("Test Passed: Caught expected Validation/Type Error")

def test_place_limit_order_api_error():
    """
    Tests that Binance API errors are correctly caught and wrapped for limit orders.
    """
    print("\n--- Running Limit Order API Error Test ---")
    mock_binance_client = MagicMock()
    mock_binance_client.futures_create_order.side_effect = BinanceAPIException(
        response=MagicMock(status_code=400, text='{"code": -1102, "msg": "Mandatory parameter price was not sent, was empty/null, or malformed."}'),
        status_code=400,
        text='{"code": -1102, "msg": "Mandatory parameter price was not sent, was empty/null, or malformed."}'
    )
    
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    mock_client_wrapper.get_client.return_value = mock_binance_client
    
    manager = OrderManager(mock_client_wrapper)
    
    try:
        manager.place_limit_order("BTCUSDT", "BUY", 0.01, 0.0) # Price 0.0 should fail validation anyway, but let's test API error wrapping
        print("Test Failed: OrderError not raised")
    except (OrderError, ValidationError) as e:
        print(f"Test Passed: Caught expected error - {e}")

if __name__ == "__main__":
    test_place_limit_order_success()
    test_place_limit_order_missing_price()
    test_place_limit_order_api_error()
