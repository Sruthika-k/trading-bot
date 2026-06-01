"""
Validation logic for trading data and configurations.
"""

from typing import Any, Dict
from bot.exceptions import ValidationError

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validates the bot configuration.

    Args:
        config: A dictionary containing configuration parameters.

    Returns:
        True if valid, raises ValidationError otherwise.

    Raises:
        ValidationError: If required configuration keys are missing or invalid.
    """
    required_keys = ["API_KEY", "API_SECRET"]
    for key in required_keys:
        if key not in config or not config[key]:
            raise ValidationError(f"Missing required configuration: {key}")
    return True

def validate_order_params(params: Dict[str, Any]) -> bool:
    """
    Validates order parameters before submission.

    Args:
        params: A dictionary of order parameters.

    Returns:
        True if valid, raises ValidationError otherwise.

    Raises:
        ValidationError: If order parameters are invalid.
    """
    # Placeholder for order validation logic
    if "symbol" not in params:
        raise ValidationError("Order must include a symbol.")
    return True
