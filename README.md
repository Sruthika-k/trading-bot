# 🚀 Binance Futures Testnet Trading Bot

A production-grade Python trading bot designed for the Binance Futures Testnet. This project implements a modular architecture with strict validation, centralized logging, and a modern CLI interface.

---

## # Project Overview

This bot provides a robust framework for executing and managing futures trades on the Binance Testnet environment. It focuses on **clean code principles**, **security**, and **observability**, making it an ideal starting point for developing automated trading strategies.

## # Features

- **Unified Order Service**: Single entry point for Market and Limit orders with automatic routing and execution polling.
- **Modern CLI**: Interactive terminal interface powered by `Typer` and `Rich` with direct argument support and high-fidelity tables.
- **Strict Validation**: Pydantic-powered models ensure all order parameters are correct before reaching the API.
- **Production Logging**: Centralized, rotating file logs with suppressed third-party noise for focused auditing.
- **Resilient Error Handling**: Granular handling for API errors, connection timeouts, and network failures.
- **Secure Configuration**: Environment-based secret management using `python-dotenv`.

## # Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd trading_bot
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## # Environment Setup

1. Copy the template environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and provide your credentials:
   ```env
   BINANCE_API_KEY=your_testnet_api_key
   BINANCE_API_SECRET=your_testnet_api_secret
   BINANCE_TESTNET=True
   LOG_LEVEL=INFO
   ```

## # Binance Futures Testnet Setup

1. Go to the [Binance Futures Testnet](https://testnet.binancefuture.com/) website.
2. Log in or register an account.
3. Locate the **API Key** section and generate a new key/secret pair.
4. Ensure your Testnet account is funded with mock USDT (usually provided automatically).

## # Running Market Orders

Market orders execute immediately at the best available price.
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

## # Running Limit Orders

Limit orders are placed at a specific price and use **GTC (Good 'Til Cancelled)** time-in-force.
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

## # Example Commands

- **Place Market Buy**:
  ```bash
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.05
  ```
- **Place Limit Sell**:
  ```bash
  python cli.py --symbol SOLUSDT --side SELL --type LIMIT --quantity 10 --price 150.5
  ```
- **View Help**:
  ```bash
  python cli.py --help
  ```

## # Logging

Logs are stored in the `logs/` directory.
- **File**: `logs/trading.log`
- **Rotation**: Max 10MB per file, keeping up to 5 historical backups.
- **Level**: Configurable via `.env` (`DEBUG`, `INFO`, etc.). Our modules log at the specified level, while noisy third-party libraries (urllib3, asyncio) are suppressed to `WARNING`.

## # Project Structure

```text
trading_bot/
├── bot/                       # Core Application Package
│   ├── __init__.py            # Package exports and versioning
│   ├── client.py              # Binance API wrapper & connection logic
│   ├── config.py              # Pydantic-based configuration management
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── logging_config.py      # Centralized rotating logging setup
│   ├── orders.py              # Unified order service & response formatting
│   └── validators.py          # Pydantic models for business rule validation
├── logs/                      # Log Storage
│   └── trading.log            # Main application runtime log file
├── tests/                     # Automated Test Suite
│   ├── __init__.py            # Test package initialization
│   ├── test_formatter.py      # Response formatting unit tests
│   ├── test_limit_orders.py   # Limit order logic tests
│   ├── test_market_orders.py  # Market order logic tests
│   ├── test_unified_orders.py # Unified service routing tests
│   └── test_validators.py     # Pydantic validation unit tests
├── cli.py                     # Typer & Rich-powered direct argument CLI
├── .env.example               # Environment template
├── .gitignore                 # Security (secrets) & maintenance exclusions
├── requirements.txt           # Project dependencies
└── README.md                  # Professional documentation & setup guide
```

## # Testing

The project includes a comprehensive test suite. Run all tests from the root directory using:
```bash
python -m unittest discover tests
```

## # Assumptions

1. **Testnet Only**: This version is strictly configured for the Binance Futures Testnet as indicated by the `BINANCE_TESTNET=True` default and explicit endpoint routing.
2. **USDT Margin**: The order logic assumes a USDT-margined futures account.
3. **Python 3.11+**: Uses modern type hinting and Pydantic features requiring Python 3.11 or higher.
4. **GTC Default**: All limit orders are assumed to be Good 'Til Cancelled.
