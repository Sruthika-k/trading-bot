"""
Unit tests for the order validation logic.
"""

import unittest
from bot.validators import validate_order_params, ValidationError

class TestOrderValidators(unittest.TestCase):
    """
    Tests for OrderValidator and associated functions.
    """

    def test_valid_market_order(self):
        """Tests that a valid market order passes validation."""
        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 0.001
        }
        self.assertTrue(validate_order_params(params))

    def test_valid_limit_order(self):
        """Tests that a valid limit order passes validation."""
        params = {
            "symbol": "ETHUSDT",
            "side": "SELL",
            "type": "LIMIT",
            "quantity": 1.5,
            "price": 2500.0
        }
        self.assertTrue(validate_order_params(params))

    def test_invalid_side(self):
        """Tests that an invalid side raises ValidationError."""
        params = {
            "symbol": "BTCUSDT",
            "side": "HOLD",  # Invalid
            "type": "MARKET",
            "quantity": 0.001
        }
        with self.assertRaises(ValidationError):
            validate_order_params(params)

    def test_missing_price_for_limit_order(self):
        """Tests that a limit order without a price raises ValidationError."""
        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": 0.001
            # price missing
        }
        with self.assertRaises(ValidationError):
            validate_order_params(params)

    def test_negative_quantity(self):
        """Tests that a negative quantity raises ValidationError."""
        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": -1.0
        }
        with self.assertRaises(ValidationError):
            validate_order_params(params)

if __name__ == "__main__":
    unittest.main()
