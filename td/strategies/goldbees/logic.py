"""/td/strategies/goldbees/logic.py"""
from td.strategies.comman.signals import build_buy_signal
from td.strategies.comman.utils import get_stock_data, position_size


def buy_logic(strategy):
    """buy logic"""
    stock = get_stock_data(strategy)
    price = stock["close"] - strategy.config.reduce
    qty = position_size(strategy, price)
    return [
        build_buy_signal(strategy, qty, price)
    ]
