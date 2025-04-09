# td/core/data/historical.py
from jugaad_data.nse import stock_df
from datetime import date, timedelta
import pandas as pd

class HistoricalData:
    def __init__(self):
        self.cache = {}

    def get_data(self, symbol, from_date, to_date, series="EQ"):
        """Fetch historical data with caching"""
        cache_key = f"{symbol}_{from_date}_{to_date}_{series}"
        
        if cache_key not in self.cache:
            df = stock_df(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                series=series
            )
            self.cache[cache_key] = df.sort_values('DATE', ascending=True)
        
        return self.cache[cache_key].copy()

    def get_last_close(self, symbol, days_back=1):
        """Get the latest closing price"""
        today = date.today()
        df = self.get_data(
            symbol=symbol,
            from_date=today - timedelta(days=days_back + 5),  # Buffer
            to_date=today
        )
        return df['CLOSE'].iloc[-days_back]