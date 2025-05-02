import argparse,os
from td.core.broker.zerodha import ZerodhaBroker
from td.core.order_manager import OrderManager
from td.core.logging.google_drive import GoogleDriveLogger
from mycolorlogger.mylogger import log
import json
from pathlib import Path
from td.core.logging.telegram import TelegramNotifier
from td.strategies import get_strategy  # Factory function to load strategies

#configration files
import importlib

def load_strategy_config(name: str):
    module_path = f"td.config.strategies.{name.lower()}"
    config_name = f"{name.upper()}_CONFIG"

    try:
        module = importlib.import_module(module_path)
        return getattr(module, config_name)
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Could not load config for strategy '{name}': {e}")


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