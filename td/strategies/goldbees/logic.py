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
    holding = get_holding(strategy)
    if not holding:
        return []
    sell_price = max(
        holding['average_price'] * strategy.config.profit_percentage,
        holding['last_price']
    )
    sell_qnt = holding['quantity']
    sell_qnt = sell_qnt if strategy.config.min_sell_qnt < sell_qnt else 0

    return [
        build_sell_signal(strategy, sell_qnt, sell_price)
    ]
