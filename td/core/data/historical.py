# td/core/data/historical.py
from jugaad_data.nse import stock_df
from datetime import date, timedelta
import pandas as pd
import hashlib

class HistoricalData:
    def __init__(self):
        self.cache = {}

    def get_data(self, broker, symbol, from_date, to_date, series="EQ"):
        """Fetch historical data using Zerodha first, fallback to Jugaad, with caching"""
        key_str = f"{symbol}_{from_date}_{to_date}_{series}"
        cache_key = hashlib.md5(key_str.encode()).hexdigest()

        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        # Try Zerodha API first
        try:
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")

            # Read instrument token from file
            nse_data = pd.read_csv("td/core/data/nse_instrument_token.csv")
            instrument_token = nse_data[nse_data.tradingsymbol == symbol].instrument_token.values[0]

            data = broker.historical_data(instrument_token, from_date_str, to_date_str, 'day')
            df = pd.DataFrame(data)
            df.columns = df.columns.str.upper()
            df['DATE'] = pd.to_datetime(df['DATE']).dt.date

            self.cache[cache_key] = df
            return df.copy()

        except Exception as e:
            print(f"[Zerodha failed] Fallback to jugaad: {e}")
            # Fallback to jugaad_data
        df = stock_df(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
            series=series
        )
        df = df.sort_values('DATE', ascending=True)
        self.cache[cache_key] = df
        return df.copy()

    def get_last_close(self, broker, symbol, days_back=1):
        """Get the latest closing price from most recent trading day"""
        today = date.today()
        df = self.get_data(
            broker=broker,
            symbol=symbol,
            from_date=today - timedelta(days=days_back + 5),  # Extra buffer
            to_date=today
        )
        return df['CLOSE'].iloc[-days_back]
