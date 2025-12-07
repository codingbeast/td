"""/td/strategies/goldbees/utils.py"""
from datetime import  datetime, timedelta
from td.strategies.comman.utils import position_size



def _get_previous_week_range():
    """get previous week range"""
    today = datetime.today()
    previous_friday = today - timedelta(days=6)
    adjusted_end_date = today + timedelta(days=1)
    return previous_friday.date(), adjusted_end_date.date()
def _check_candle_type(open_price, close_price):
    """Return 'bullish', 'bearish', or 'doji'"""
    if close_price > open_price:
        return False #bullish
    if close_price < open_price:
        return True #bearish
    return False #doji


def get_stock_data_for_candle(strategy):
    """Helper method to get required stock data"""
    start_of_week, end_of_week = _get_previous_week_range()
    client = strategy.get_data_client
    df = client.get_data(
        symbol=strategy.config.ticker,
        exchange=strategy.config.exchange,
        from_date=start_of_week,
        to_date=end_of_week,
        series="EQ"
    )
    stock ={}
    open_price = df.iloc[0]['OPEN']
    close_price = df.iloc[-1]['CLOSE']
    high_price = max(df['HIGH'])
    low_price = min(df['LOW'])
    stock['open_price']  = open_price
    stock['close_price'] = close_price
    stock['high_price']  = high_price
    stock['low_price']   = low_price
    stock['qnt'] = position_size(strategy, stock_price=close_price)
    stock['isBearish'] = _check_candle_type(open_price=open_price, close_price=close_price)
    return stock
