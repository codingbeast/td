import importlib
import argparse,os
from td.core.broker.zerodha import ZerodhaBroker
from td.core.order_manager import OrderManager
from td.core.logging.google_drive import GoogleDriveLogger
from mycolorlogger.mylogger import log
import json
from pathlib import Path
from td.core.logging.telegram import TelegramNotifier
from td.strategies import get_strategy  # Factory function to load strategies

def load_strategy_config(name: str):
    """
    Load strategy configuration from:
        config/strategies/<name>.json
    
    This function keeps the SAME API as before but is now JSON + Pydantic based.
    """

    # Resolve project root (load from your config folder)
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

    # Load raw JSON data
    raw = json.loads(json_path.read_text(encoding="utf-8"))

    # Load Pydantic model dynamically
    try:
        model_module = importlib.import_module(f"config.models_config.{name.lower()}")
        config_class = getattr(model_module, f"{name.capitalize()}Config")
    except Exception as e:
        raise ValueError(f"Could not load Pydantic model for {name}: {e}")

    # Validate JSON with Pydantic model
    return config_class(**raw)



def main():
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--strategy', required=True, help='Strategy name')
    parser.add_argument('--action', choices=['buy', 'sell','buy-sell', 'check'], required=True)
    args = parser.parse_args()
    
    # Initialize components
    logger = GoogleDriveLogger()
    message_logger = log.logger
    notifier = TelegramNotifier(
        token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_USER_ID'),
    )
    broker = ZerodhaBroker(
        user_id=os.getenv('ZERODHA_USER_ID'),
        password=os.getenv('ZERODHA_USER_PASSWORD'),
        tpin_token=os.getenv('ZERODHA_TPIN_TOKEN')
    )
    order_manager = OrderManager(broker, logger, message_logger, notifier)

    #Load confi strategy
    # Load strategy
    strategy_config = load_strategy_config(args.strategy)
    strategy = get_strategy(args.strategy, strategy_config)
    strategy.current_action = args.action
    # Execute based on action
    if args.action == 'buy':
        order_manager.execute_strategy_orders(strategy)
    if args.action == 'buy-sell':
        order_manager.execute_strategy_orders(strategy)
    elif args.action == 'sell':
        order_manager.execute_strategy_orders(strategy)
    elif args.action == 'check':
        order_manager.execute_strategy_orders(strategy)

if __name__ == "__main__":
    main()