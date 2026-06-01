"""
Test script to simulate market order placement and verify response handling.
"""

import logging
from unittest.mock import MagicMock
from bot.orders import OrderManager
from bot.client import BinanceClient
from bot.exceptions import OrderError, ValidationError

# Setup basic logging for the test
logging.basicConfig(level=logging.DEBUG)

def test_place_market_order_success():
    """
    Tests successful market order placement with a mocked Binance client.
    """
    print("\n--- Running Success Test ---")
    mock_binance_client = MagicMock()
    mock_binance_client.futures_create_order.return_value = {
        "symbol": "BTCUSDT",
        "orderId": "12345",
        "status": "FILLED",
        "side": "BUY",
        "type": "MARKET"
    }
    
    # Mock BinanceClient wrapper
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    mock_client_wrapper.get_client.return_value = mock_binance_client
    
    manager = OrderManager(mock_client_wrapper)
    
    try:
        response = manager.place_market_order("BTCUSDT", "BUY", 0.001)
        print(f"Test Passed: Received OrderID {response.get('orderId')}")
    except Exception as e:
        print(f"Test Failed: Unexpected exception {e}")

def test_place_market_order_validation_error():
    """
    Tests that invalid inputs raise a ValidationError.
    """
    print("\n--- Running Validation Error Test ---")
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    manager = OrderManager(mock_client_wrapper)
    
    try:
        # Invalid side 'HOLD'
        manager.place_market_order("BTCUSDT", "HOLD", 0.001)
        print("Test Failed: ValidationError not raised for invalid side")
    except ValidationError:
        print("Test Passed: Caught expected ValidationError")
    except Exception as e:
        print(f"Test Failed: Caught unexpected exception type {type(e)}")

def test_place_market_order_api_error():
    """
    Tests that Binance API errors are correctly caught and wrapped in OrderError.
    """
    print("\n--- Running API Error Test ---")
    from binance.exceptions import BinanceAPIException
    
    mock_binance_client = MagicMock()
    # Simulate a Binance API exception
    mock_binance_client.futures_create_order.side_effect = BinanceAPIException(
        response=MagicMock(status_code=400, text='{"code": -2010, "msg": "Account has insufficient balance."}'),
        status_code=400,
        text='{"code": -2010, "msg": "Account has insufficient balance."}'
    )
    
    mock_client_wrapper = MagicMock(spec=BinanceClient)
    mock_client_wrapper.get_client.return_value = mock_binance_client
    
    manager = OrderManager(mock_client_wrapper)
    
    try:
        manager.place_market_order("BTCUSDT", "BUY", 100.0)
        print("Test Failed: OrderError not raised for insufficient balance")
    except OrderError as e:
        print(f"Test Passed: Caught expected OrderError - {e}")

if __name__ == "__main__":
    test_place_market_order_success()
    test_place_market_order_validation_error()
    test_place_market_order_api_error()
