"""
Command-line interface for the Binance Futures Testnet trading bot.
Accepts direct arguments for order placement as per assignment requirements.
"""

import logging
from typing import Any, Dict, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich import print as rprint

from bot import (
    get_config,
    setup_logging,
    BinanceClient,
    OrderManager,
    TradingBotError,
    ValidationError,
    NetworkError,
    ConfigurationError
)
from bot.validators import OrderSide, OrderType

# Initialize Rich console
console = Console()

def display_order_request(symbol: str, side: str, order_type: str, quantity: float, price: Optional[float]):
    """Displays a visually appealing table of the order request."""
    table = Table(
        title="[bold blue]ORDER REQUEST[/bold blue]", 
        show_header=True, 
        header_style="bold white on blue",
        box=box.ROUNDED
    )
    table.add_column("Parameter", style="dim", width=15)
    table.add_column("Value", style="bold cyan")
    
    table.add_row("Symbol", symbol.upper())
    table.add_row("Side", side.upper())
    table.add_row("Type", order_type.upper())
    table.add_row("Quantity", f"{quantity:g}")
    if price:
        table.add_row("Price", f"{price:,.2f}")
    else:
        table.add_row("Price", "[dim]Market[/dim]")
    
    console.print("\n", table)

def display_order_response(response: Dict[str, Any]):
    """Displays a visually appealing table of the order response."""
    table = Table(
        title="[bold green]ORDER RESPONSE[/bold green]", 
        show_header=True, 
        header_style="bold white on green",
        box=box.ROUNDED
    )
    table.add_column("Field", style="dim", width=15)
    table.add_column("Value", style="bold yellow")
    
    # Use formatted response fields safely
    table.add_row("Order ID", str(response.get("order_id", "N/A")))
    table.add_row("Status", response.get("status", "UNKNOWN"))
    table.add_row("Executed Qty", str(response.get("executed_qty", "0")))
    table.add_row("Avg Price", f"{float(response.get('avg_price', 0)):,.2f}")
    
    console.print(table, "\n")

def main(
    symbol: str = typer.Option(..., "--symbol", help="Trading pair (e.g., BTCUSDT)"),
    side: OrderSide = typer.Option(..., "--side", help="Order side (BUY or SELL)"),
    order_type: OrderType = typer.Option(OrderType.MARKET, "--type", help="Order type (MARKET or LIMIT)"),
    quantity: float = typer.Option(..., "--quantity", help="Quantity to trade"),
    price: Optional[float] = typer.Option(None, "--price", help="Limit price (required for LIMIT orders)"),
):
    """
    � Binance Futures Testnet Trading Bot CLI
    
    Submit orders directly using command-line arguments.
    """
    try:
        # 1. Load configuration and setup logging
        config = get_config()
        setup_logging(config.log_level)
        logger = logging.getLogger(__name__)

        # 2. Display order request summary
        display_order_request(symbol, side, order_type, quantity, price)

        # 3. Initialize client and manager
        with console.status("[bold green]Connecting to Binance...") as status:
            client = BinanceClient(
                api_key=config.binance_api_key,
                api_secret=config.binance_api_secret,
                testnet=config.binance_testnet
            )
            order_manager = OrderManager(client)
            
            status.update("[bold blue]Executing order...")
            response = order_manager.place_order(
                symbol=symbol,
                side=side.value,
                order_type=order_type.value,
                quantity=quantity,
                price=price
            )

        # 4. Display response details
        display_order_response(response)
        rprint("[bold green]✅ Order processed successfully.[/bold green]")

    except ValidationError as e:
        rprint(Panel(f"[bold red]Validation Error:[/bold red] {e}", border_style="red", title="Error"))
        raise typer.Exit(code=1)
    except NetworkError as e:
        rprint(Panel(f"[bold red]Network/Connection Error:[/bold red] {e}\nPlease check your internet connection or Binance service status.", border_style="red", title="Network Error"))
        raise typer.Exit(code=1)
    except ConfigurationError as e:
        rprint(Panel(f"[bold red]Configuration Error:[/bold red] {e}\nPlease check your .env file and API credentials.", border_style="red", title="Config Error"))
        raise typer.Exit(code=1)
    except TradingBotError as e:
        rprint(Panel(f"[bold red]Trading Error:[/bold red] {e}", border_style="red", title="Error"))
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(Panel(f"[bold red]Unexpected Error:[/bold red] {e}", border_style="red", title="Critical Error"))
        raise typer.Exit(code=1)

if __name__ == "__main__":
    typer.run(main)
