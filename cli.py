"""
Main entry point for the Binance Futures Testnet trading bot CLI.
"""

import logging
from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import OrderManager
from bot.config import get_config
from bot.exceptions import ConfigurationError

def main() -> None:
    """
    Main function to initialize and run the trading bot.
    """
    try:
        # Load and validate configuration
        config = get_config()
        
        # Setup logging
        setup_logging(config.log_level)
        logger = logging.getLogger(__name__)

        # Initialize client and order manager
        client = BinanceClient(
            api_key=config.binance_api_key,
            api_secret=config.binance_api_secret,
            testnet=config.binance_testnet
        )
        order_manager = OrderManager(client)

        logger.info("Trading bot started successfully.")
        
    except ConfigurationError as e:
        # Catch specific configuration errors
        print(f"Configuration Error: {e}")
        exit(1)
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
