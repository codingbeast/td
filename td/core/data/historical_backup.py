# td/core/data/historical.py
from jugaad_data.nse import stock_df
from datetime import date, timedelta
import pandas as pd
import hashlib


# td/core/data/historical.py
from jugaad_data.nse import stock_df
from datetime import date, timedelta
import pandas as pd
import hashlib
# import yfinance as yf

# class HistoricalData:
#     def __init__(self):
#         self.cache = {}

#     def get_data(self, symbol, from_date, to_date, series="EQ"):
#         """Fetch historical data with caching and Yahoo fallback"""
#         key_str = f"{symbol}_{from_date}_{to_date}_{series}"
#         cache_key = hashlib.md5(key_str.encode()).hexdigest()

#         if cache_key not in self.cache:
#             try:
#                 # Try fetching from NSE
#                 df = stock_df(
#                     symbol=symbol,
#                     from_date=from_date,
#                     to_date=to_date,
#                     series=series
#                 )

#                 if df.empty:
#                     raise ValueError("Empty DataFrame from NSE")

#             except Exception as e:
#                 print(f"[WARNING] NSE data fetch failed: {e}. Falling back to Yahoo Finance...")

#                 # Use Yahoo Finance fallback
#                 yf_symbol = f"{symbol}.NS"
#                 df = yf.download(
#                     yf_symbol,
#                     start=from_date.strftime("%Y-%m-%d"),
#                     end=(to_date + timedelta(days=1)).strftime("%Y-%m-%d"),  # include end date
#                     progress=False,
#                     auto_adjust=True, 
#                     multi_level_index=False
#                 )

#                 if df.empty:
#                     raise ValueError("Yahoo Finance fallback also failed")

#                 # Format Yahoo data to match jugaad_data format
#                 df.reset_index(inplace=True)
#                 df.columns = [col.upper() for col in df.columns]
#                 df = df[["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]

#             # Sort and cache
#             df = df.sort_values('DATE', ascending=True)
#             self.cache[cache_key] = df

#         return self.cache[cache_key].copy()

#     def get_last_close(self, symbol, days_back=1):
#         """Get the latest closing price"""
#         today = date.today()
#         df = self.get_data(
#             symbol=symbol,
#             from_date=today - timedelta(days=days_back + 5),
#             to_date=today
#         )
#         return df['CLOSE'].iloc[-days_back]


class HistoricalData:
    def __init__(self):
        self.cache = {}

    def get_data(self, symbol, from_date, to_date, series="EQ"):
        """Fetch historical data with caching"""
        key_str = f"{symbol}_{from_date}_{to_date}_{series}"
        cache_key = hashlib.md5(key_str.encode()).hexdigest()
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