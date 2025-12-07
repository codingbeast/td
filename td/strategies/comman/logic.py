"""td/strategies/comman/logic.py"""
from td.strategies.comman.signals import build_sell_signal
from td.strategies.comman.utils import get_holding

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
