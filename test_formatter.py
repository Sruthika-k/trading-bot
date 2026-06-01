"""
Unit tests for the order response formatter.
"""

import unittest
from bot.orders import format_order_response

class TestResponseFormatter(unittest.TestCase):
    """
    Tests for the format_order_response function.
    """

    def test_format_complete_response(self):
        """Tests formatting with a complete Binance response."""
        raw_response = {
            "orderId": 12345,
            "status": "FILLED",
            "executedQty": "0.5",
            "avgPrice": "50000.0",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT"
        }
        formatted = format_order_response(raw_response)
        
        self.assertEqual(formatted["order_id"], 12345)
        self.assertEqual(formatted["status"], "FILLED")
        self.assertEqual(formatted["executed_qty"], 0.5)
        self.assertEqual(formatted["avg_price"], 50000.0)
        self.assertEqual(formatted["symbol"], "BTCUSDT")

    def test_format_missing_fields_safely(self):
        """Tests formatting with missing fields to ensure safe defaults."""
        raw_response = {
            "orderId": 67890,
            "status": "NEW",
            "origQty": "1.0",
            "price": "2000.0"
            # executedQty and avgPrice missing
        }
        formatted = format_order_response(raw_response)
        
        self.assertEqual(formatted["order_id"], 67890)
        self.assertEqual(formatted["status"], "NEW")
        # Should fallback to origQty and price
        self.assertEqual(formatted["executed_qty"], 1.0)
        self.assertEqual(formatted["avg_price"], 2000.0)
        self.assertEqual(formatted["symbol"], "N/A")

    def test_format_empty_response(self):
        """Tests formatting with an empty dictionary."""
        formatted = format_order_response({})
        
        self.assertEqual(formatted["order_id"], "N/A")
        self.assertEqual(formatted["status"], "UNKNOWN")
        self.assertEqual(formatted["executed_qty"], 0.0)
        self.assertEqual(formatted["avg_price"], 0.0)

if __name__ == "__main__":
    unittest.main()
