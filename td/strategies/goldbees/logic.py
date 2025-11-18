"""/td/strategies/goldbees/logic.py"""
from .signals import build_buy_signal, build_sell_signal
from .utils import get_stock_data, get_holding, position_size


def buy_logic(strategy):
    """buy logic"""
    stock = get_stock_data(strategy)
    qty = position_size(strategy, stock)
    price = stock["close"] - strategy.config.reduce

    return [
        build_buy_signal(strategy, qty, price)
    ]


def sell_logic(strategy):
    """sell logic"""
    hold = get_holding(strategy)
    if not hold:
        return []

    stock = get_stock_data(strategy)
    qty = hold["quantity"]
    price = stock["close"]

    return [
        build_sell_signal(strategy, qty, price)
    ]
