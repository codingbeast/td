"""/td/strategies/hommagenius/logic.py"""
from td.core.logging.console_logger import log
from .signals import build_buy_signal, build_sell_signal
from .utils import get_holding, get_stock_data_for_candle

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


def sell_logic(strategy):
    """sell logic"""
    holding = get_holding(strategy)
    if not holding:
        return []
    sell_price = max(
        holding['average_price'] * strategy.config.profit_percentage,
        holding['last_price']
    )
    sell_qnt = holding['quantity']
    sell_qnt = sell_qnt if strategy.config.min_sell_qnt < sell_qnt else 0
    #stock = get_stock_data(strategy)
    #price = stock["close"]
    return [
        build_sell_signal(strategy, sell_qnt, sell_price)
    ]
