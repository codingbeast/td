"""/td/strategies/goldbees/logic.py"""
from td.strategies.comman.signals import build_buy_signal
from td.strategies.comman.utils import get_stock_data, position_size
from td.strategies.lahari.utils import is_stock_in_position


def buy_logic(strategy):
    """buy logic"""
    stock = get_stock_data(strategy)
    price = stock["close"] - strategy.config.reduce
    qty = position_size(strategy, price)
    return [
        build_buy_signal(strategy, qty, price)
    ]

def check_logic(strategy):
    """check logic"""
    is_in_position = is_stock_in_position(strategy)
    if is_in_position:
        return []
    return buy_logic(strategy)
