"""Main script to run trading strategies using the NEW modular Pydantic framework."""
# pylint: disable=broad-exception-caught
import argparse
import importlib
import json
import os
from pathlib import Path
from td.core.order_manager import OrderManager
from td.core.engine import Engine
from td.core.logging.console_logger import log
from td.core.logging.google_drive import GoogleDriveLogger
from td.core.logging.telegram import TelegramNotifier
from td.core.broker.zerodha import ZerodhaBroker


def load_strategy_config(name: str):
    """
    Load strategy configuration from:
        config/strategies/<name>.json
    And validate using:
        td/config/models_config/<name>.py
    """

    # Resolve project root
    start_path = Path(__file__).resolve().parent
    project_root = start_path

    # Walk upward until we find "config"
    while not (project_root / "config").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    if not (project_root / "config").exists():
        raise RuntimeError("Could not locate 'config' directory!")

    config_dir = project_root / "config" / "strategies"
    json_path = config_dir / f"{name.lower()}.json"

    if not json_path.exists():
        raise FileNotFoundError(
            f"Config JSON not found: {json_path}\n"
            f"Expected: config/strategies/{name.lower()}.json"
        )

    # Load raw JSON
    raw = json.loads(json_path.read_text(encoding="utf-8"))

    # Import Pydantic Config Model dynamically
    try:
        model_module = importlib.import_module(f"td.config.models_config.{name.lower()}")
        config_class = getattr(model_module, f"{name.capitalize()}Config")
    except Exception as e:
        raise ValueError(f"Could not load Pydantic model for {name}: {e}") from e

    return config_class(**raw)


def load_broker():
    """Load Zerodha broker via Environment Variables."""
    zerodha_user = os.getenv("ZERODHA_USER_ID")
    zerodha_password = os.getenv("ZERODHA_USER_PASSWORD")
    zerodha_tpin = os.getenv("ZERODHA_TPIN_TOKEN")

    if not zerodha_user or not zerodha_password or not zerodha_tpin:
        raise ValueError(
            "Missing Zerodha credentials. Set:\n"
            "ZERODHA_USER_ID, ZERODHA_USER_PASSWORD, ZERODHA_TPIN_TOKEN"
        )

    return ZerodhaBroker(
        user_id=zerodha_user,
        password=zerodha_password,
        tpin_token=zerodha_tpin,
    )


def main():
    """Run trading strategy."""
    parser = argparse.ArgumentParser(description="Run trading strategy")
    parser.add_argument("--strategy", required=True, help="Strategy name (Goldbees, CPSE, etc.)")
    parser.add_argument("--action", choices=["buy", "sell", "buy-sell", "check"], required=True)
    args = parser.parse_args()

    strategy_name = args.strategy.capitalize()
    log.info("Running strategy: %s", strategy_name)

    # 1. Load config (already validated)
    config_model = load_strategy_config(strategy_name)

    # 2. Load broker
    broker = load_broker()

    # 3. Placeholder for market data
    data = {}

    # 4. Initialize engine
    engine = Engine(config_model, data)

    # 5. Create strategy (no arguments needed)
    strategy = engine.create_strategy()

    # 6. Attach broker & action
    strategy.set_broker(broker)
    strategy.current_action = args.action

    # 7. Run strategy
    log.info("Executing action: %s", args.action)
    # signal = strategy.generate_signals()
    # log.info("Final signal: %s", signal)

    # Instantiate supporting components required by OrderManager
    drive_logger = GoogleDriveLogger()
    message_logger = log
    notifier = TelegramNotifier(
        token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_USER_ID'),
    )

    # Create OrderManager instance and execute orders
    order_manager = OrderManager(broker, drive_logger, message_logger, notifier)
    order_manager.execute_strategy_orders(strategy)


if __name__ == "__main__":
    main()
