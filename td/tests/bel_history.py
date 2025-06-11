# bel_history.py
from datetime import date, timedelta
from nse import NSE
from pathlib import Path
import pandas as pd
# Working directory
DIR = Path(__file__).parent

def fetch_bel_data():
    nse = NSE(download_folder=DIR)
    status = nse.status()
    today = date.today()
    end_date = today - timedelta(days=10)
    data = nse.fetch_equity_historical_data(symbol="BEL",from_date=end_date, to_date=today , series="EQ")
    df = pd.DataFrame(data)
    df = df[['mTIMESTAMP',
            'CH_SERIES',
            'CH_OPENING_PRICE',
            'CH_TRADE_HIGH_PRICE',
            'CH_TRADE_LOW_PRICE',
            'CH_PREVIOUS_CLS_PRICE',
            'CH_LAST_TRADED_PRICE',
            'CH_CLOSING_PRICE',
            'VWAP',
            'CH_52WEEK_HIGH_PRICE',
            'CH_52WEEK_LOW_PRICE',
            'CH_TOT_TRADED_QTY',
            'CH_TOTAL_TRADES',
            'CH_SYMBOL'
            ]]
    df = df.rename(columns={
        'mTIMESTAMP': 'DATE',
        'CH_SERIES': 'SERIES',
        'CH_OPENING_PRICE': 'OPEN',
        'CH_TRADE_HIGH_PRICE': 'HIGH',
        'CH_TRADE_LOW_PRICE': 'LOW',
        'CH_PREVIOUS_CLS_PRICE': 'PREV. CLOSE',
        'CH_LAST_TRADED_PRICE': 'LTP',
        'CH_CLOSING_PRICE': 'CLOSE',
        'VWAP': 'VWAP',
        'CH_52WEEK_HIGH_PRICE': '52W H',
        'CH_52WEEK_LOW_PRICE': '52W L',
        'CH_TOT_TRADED_QTY': 'VOLUME',
        'CH_TOTAL_TRADES': 'NO OF TRADES',
        'CH_SYMBOL': 'SYMBOL'
    })
    df['DATE'] = pd.to_datetime(df['DATE'])
    nse.exit() 
    print(df)
if __name__ == "__main__":
    fetch_bel_data()
