"""/td/strategies/goldbees/utils.py"""
from datetime import date, timedelta


def get_stock_data(strategy):
    """get stock data"""
    client = strategy.get_data_client
    today = date.today()

    df = client.get_data(
        symbol=strategy.config.ticker,
        from_date=today - timedelta(days=10),
        to_date=today,
        series="EQ"
    )

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


def position_size(strategy, stock):
    """"get position size"""
    price = stock["close"] - strategy.config.reduce
    amt = strategy.config.amount

    if strategy.config.amount_strict:
        return int(amt // price)
    return int(-(-amt // price))  # math.ceil
