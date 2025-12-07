"""/td/strategies/lahari/utils.py"""
from datetime import  date, timedelta
from typing import Optional
from td.core.logging.console_logger import log

def calculate_total_shares(strategy, total_price, stock_price):
    """calculate total share prices"""
    if strategy.config.amount_strict:
        return int(total_price // stock_price) #math.floor
    return int(-(-total_price // stock_price))  # math.ceil

def get_stock_data(strategy) -> list:
    """get stock data"""
    client = strategy.get_data_client
    today = date.today()

    df = client.get_data(
        symbol=strategy.config.ticker,
        exchange=strategy.config.exchange,
        from_date=today - timedelta(days=30),
        to_date=today,
        series="EQ"
    )
    df.sort_values(by='DATE', ascending=True, inplace=True)
    last_15_rows = df.tail(15)
    return last_15_rows

def get_holding(strategy):
    """get holding """
    if strategy.broker is None:
        return None
    holdings = strategy.broker.get_holdings()
    return next(
        (h for h in holdings if h["tradingsymbol"] == strategy.config.ticker),
        None
    )

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
