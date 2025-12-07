"""/td/strategies/hommagenius/logic.py"""
from td.core.logging.console_logger import log
from td.strategies.comman.signals import build_buy_signal
from .utils import get_stock_data_for_candle

def buy_logic(strategy):
    """buy logic"""
    stock_data = get_stock_data_for_candle(strategy)
    qty = stock_data['qnt']
    price = stock_data['close_price']
    if stock_data['isBearish'] is True:
        return [
            build_buy_signal(strategy, qty, price)
        ]
    log.info("No BUY signal generated as candle is not bearish.")
    return []
