"""
Unified test script to verify the refactored place_order service function.
"""

import logging
from unittest.mock import MagicMock
from bot.orders import OrderManager
from bot.client import BinanceClient
from bot.exceptions import OrderError, ValidationError

# Setup basic logging for the test
logging.basicConfig(level=logging.DEBUG)

def test_unified_place_order_market():
    """Tests placing a market order through the unified place_order function."""
    print("\n--- Testing Unified Place Order (MARKET) ---")
    mock_binance_client = MagicMock()
    mock_binance_client.futures_create_order.return_value = {
        "symbol": "BTCUSDT",
        "orderId": "1001",
        "status": "FILLED",
        "type": "MARKET"
    }
    
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    mock_client_wrapper.get_client.return_value = mock_binance_client
    
    manager = OrderManager(mock_client_wrapper)
    
    response = manager.place_order("BTCUSDT", "BUY", "MARKET", 0.001)
    print(f"Test Passed: MARKET OrderID {response.get('orderId')}")
    assert response["type"] == "MARKET"

def test_unified_place_order_limit():
    """Tests placing a limit order through the unified place_order function."""
    print("\n--- Testing Unified Place Order (LIMIT) ---")
    mock_binance_client = MagicMock()
    mock_binance_client.futures_create_order.return_value = {
        "symbol": "ETHUSDT",
        "orderId": "2002",
        "status": "NEW",
        "type": "LIMIT",
        "timeInForce": "GTC"
    }
    
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    mock_client_wrapper.get_client.return_value = mock_binance_client
    
    manager = OrderManager(mock_client_wrapper)
    
    response = manager.place_order("ETHUSDT", "SELL", "LIMIT", 1.0, 2000.0)
    print(f"Test Passed: LIMIT OrderID {response.get('orderId')}")
    assert response["type"] == "LIMIT"
    assert response["timeInForce"] == "GTC"

def test_unified_place_order_validation_failure():
    """Tests validation failure in the unified place_order function."""
    print("\n--- Testing Unified Place Order (VALIDATION FAILURE) ---")
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    manager = OrderManager(mock_client_wrapper)
    
    try:
        # Missing price for LIMIT order
        manager.place_order("BTCUSDT", "BUY", "LIMIT", 0.01)
        print("Test Failed: ValidationError not raised")
    except ValidationError:
        print("Test Passed: Caught expected ValidationError")

if __name__ == "__main__":
    test_unified_place_order_market()
    test_unified_place_order_limit()
    test_unified_place_order_validation_failure()
