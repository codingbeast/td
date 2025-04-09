import argparse,os
from td.core.broker.zerodha import ZerodhaBroker
from td.core.order_manager import OrderManager
from td.core.logging.google_drive import GoogleDriveLogger
from td.core.logging.telegram import TelegramNotifier
from td.strategies import get_strategy  # Factory function to load strategies
import json
from pathlib import Path

def load_config(strategy_name: str) -> dict:
    """Load strategy configuration from JSON file"""
    config_path = Path(__file__).parent.parent / 'config' / 'strategies' / f'{strategy_name}.json'
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config for {strategy_name}: {e}")
    
def main():
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--strategy', required=True, help='Strategy name')
    parser.add_argument('--action', choices=['buy', 'sell','buy-sell', 'check'], required=True)
    args = parser.parse_args()
    
    # Initialize components
    logger = GoogleDriveLogger()
    notifier = TelegramNotifier(
        token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_USER_ID'),
    )
    broker = ZerodhaBroker(
        user_id=os.getenv('ZERODHA_USER_ID'),
        password=os.getenv('ZERODHA_USER_PASSWORD'),
        tpin_token=os.getenv('ZERODHA_TPIN_TOKEN')
    )
    order_manager = OrderManager(broker, logger)

    #Load confi strategy
    strategy_config = load_config(args.strategy)
    # Load strategy
    strategy = get_strategy(args.strategy, strategy_config)
    
    # Execute based on action
    if args.action == 'buy':
        order_manager.execute_strategy_orders(strategy)
    if args.action == 'buy-sell':
        order_manager.execute_strategy_orders(strategy)
    elif args.action == 'sell':
        # Handle sell logic
        pass
    elif args.action == 'check':
        # Handle check logic
        pass

if __name__ == "__main__":
    main()