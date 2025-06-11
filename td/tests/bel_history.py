# bel_history.py
import yfinance as yf

def fetch_bel_data():
    bel = yf.Ticker("BEL.NS")
    hist = bel.history(period="1mo")  # Get 1 month of historical data
    print("=== BEL Historical Data (Last 1 Month) ===")
    print(hist)

if __name__ == "__main__":
    fetch_bel_data()
