"""
Validation logic for trading data and configurations using Pydantic.
Provides reusable validation models and functions for orders and configurations.
"""

import logging
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError as PydanticValidationError
from bot.exceptions import ValidationError

logger = logging.getLogger(__name__)

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderValidator(BaseModel):
    """
    Pydantic model for validating Binance Futures order parameters.
    """
    symbol: str = Field(..., min_length=1)
    side: OrderSide
    order_type: OrderType = Field(..., alias="type")
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_price_for_limit_order(self) -> "OrderValidator":
        """
        Ensures that price is provided if the order type is LIMIT.
        """
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise ValueError("Price is required for LIMIT orders.")
        return self

def validate_order_params(params: Dict[str, Any]) -> bool:
    """
    Validates order parameters against the OrderValidator model.

    Args:
        params: A dictionary of order parameters.

    Returns:
        True if valid, raises ValidationError otherwise.

    Raises:
        ValidationError: If order parameters are invalid.
    """
    try:
        OrderValidator(**params)
        return True
    except PydanticValidationError as e:
        error_msg = f"Order validation failed: {e}"
        logger.error(error_msg)
        raise ValidationError(error_msg) from e

def validate_symbol(symbol: Any) -> str:
    """
    Reusable function to validate a trading symbol.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValidationError(f"Invalid symbol: {symbol}. Must be a non-empty string.")
    return symbol.strip().upper()

def validate_quantity(quantity: Any) -> float:
    """
    Reusable function to validate order quantity.
    """
    try:
        val = float(quantity)
        if val <= 0:
            raise ValueError
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity: {quantity}. Must be a positive number.")

def validate_price(price: Any) -> float:
    """
    Reusable function to validate order price.
    """
    try:
        val = float(price)
        if val <= 0:
            raise ValueError
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid price: {price}. Must be a positive number.")
