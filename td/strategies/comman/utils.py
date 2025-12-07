"""/td/strategies/comman/utils.py"""
from datetime import  date, timedelta
from pandas import DataFrame

def _get_data(strategy, days : int = 10) -> DataFrame:
    client = strategy.get_data_client
    today = date.today()

    df = client.get_data(
        symbol=strategy.config.ticker,
        exchange=strategy.config.exchange,
        from_date=today - timedelta(days=days),
        to_date=today,
        series="EQ"
    )
    return df

def get_stock_data_with_days(strategy, days = 10):
    """get stock data with days"""
    df = _get_data(strategy, days=days)
    return df
def get_stock_data(strategy):
    """get stock data"""
    df = _get_data(strategy)
    return {
        "close": df["CLOSE"].iloc[-1],
        "high": df["HIGH"].iloc[-1],
        "low": df["LOW"].iloc[-1],
        "date": df["DATE"].iloc[-1],
    }


def get_holding(strategy):
    """get holding """
    if strategy.broker is None:
        return None
    holdings = strategy.broker.get_holdings()
    return next(
        (h for h in holdings if h["tradingsymbol"] == strategy.config.ticker),
        None
    )

def position_size(strategy, stock_price):
    """"get position size"""
    amt = strategy.config.amount
    if strategy.config.amount_strict:
        return int(strategy.config.amount // stock_price) #math.floor
    return int(-(-amt // stock_price))  # math.ceil
