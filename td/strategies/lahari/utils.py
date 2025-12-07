"""/td/strategies/lahari/utils.py"""
from typing import Optional
from pandas import DataFrame
from td.core.logging.console_logger import log
from td.strategies.comman.utils import get_stock_data_with_days

def calculate_total_shares(strategy, total_price, stock_price):
    """calculate total share prices"""
    if strategy.config.amount_strict:
        return int(total_price // stock_price) #math.floor
    return int(-(-total_price // stock_price))  # math.ceil

def get_stock_data(strategy) -> DataFrame:
    """get stock data"""
    df = get_stock_data_with_days(strategy, days=15)
    df.sort_values(by='DATE', ascending=True, inplace=True)
    last_15_rows = df.tail(15)
    return last_15_rows

def is_stock_in_position(strategy) -> Optional[bool]:
    """get positions"""
    if strategy.broker is None:
        return None
    positions = strategy.broker.get_positions().get("net",{})
    for position in positions:
        if position["tradingsymbol"] == strategy.config.ticker:
            log.info("stock code %s is already in positions", strategy.config.ticker)
            return False
        return True
    return None
