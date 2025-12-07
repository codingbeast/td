"""td/news/promoter.py"""

from datetime import datetime, timedelta
from io import StringIO
import gzip
import zlib
import brotli
import requests
import pytz
import pandas as pd
from td.core.notifier_service import get_notifier



IST = pytz.timezone("Asia/Kolkata")

# Copy-accurate browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) \
        Gecko/20100101 Firefox/145.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-insider-trading-plan",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
}


def localize_ist(dt):
    """Convert naive datetime to IST-aware datetime."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return IST.localize(dt)
    return dt.astimezone(IST)


def get_ist_yesterday():
    """get yesterday"""
    now_ist = datetime.now(IST)
    return (now_ist - timedelta(days=1)).date()


def safe_decompress(response: requests.Response) -> str:
    """safe decompress"""
    encoding = response.headers.get("Content-Encoding", "").lower()
    raw = response.raw.read()

    if "br" in encoding:
        try:
            return brotli.decompress(raw).decode("utf-8")
        except brotli.error:
            return response.text

    if "gzip" in encoding:
        try:
            return gzip.decompress(raw).decode("utf-8")
        except (OSError, zlib.error):
            return response.text

    if "deflate" in encoding:
        try:
            return zlib.decompress(raw).decode("utf-8")
        except zlib.error:
            try:
                return zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8")
            except zlib.error:
                return response.text

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return response.text


def fetch_csv_text() -> str:
    """fetch csv text"""
    session = requests.Session()

    session.get("https://www.nseindia.com", headers=HEADERS, timeout=20)
    session.get(
        "https://www.nseindia.com/companies-listing/corporate-filings-insider-trading-plan",
        headers=HEADERS,
        timeout=20
    )

    response = session.get(
        "https://www.nseindia.com/api/corporate-insider-plan?index=equities&csv=true",
        headers=HEADERS,
        timeout=20,
        stream=True
    )
    response.raise_for_status()

    return safe_decompress(response)


def extract_news() -> pd.DataFrame:
    """extract news"""
    text = fetch_csv_text()

    if text.startswith("\ufeff"):
        text = text.replace("\ufeff", "", 1)

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    df = pd.read_csv(StringIO(text), engine="python", on_bad_lines="skip")

    # Clean column names
    df.columns = (
        df.columns
        .str.replace("\n", "", regex=False)
        .str.replace("\r", "", regex=False)
        .str.replace("\ufeff", "", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Convert datetime
    df["BROADCAST DATE/TIME"] = pd.to_datetime(df["BROADCAST DATE/TIME"],
                                               format="%d-%b-%Y %H:%M:%S", errors="coerce")
    df["EXCHANGE DISSEMINATION TIME"] = pd.to_datetime(df["EXCHANGE DISSEMINATION TIME"],
                                                       format="%d-%b-%Y %H:%M:%S", errors="coerce")

    # Localize to IST
    df["BROADCAST DATE/TIME"] = df["BROADCAST DATE/TIME"].apply(localize_ist)
    df["EXCHANGE DISSEMINATION TIME"] = df["EXCHANGE DISSEMINATION TIME"].apply(localize_ist)

    # Clean strings
    for col in df.columns:
        if col not in ("BROADCAST DATE/TIME", "EXCHANGE DISSEMINATION TIME"):
            df[col] = df[col].astype(str).str.strip()

    return df


def filter_yesterday_news(df):
    """Filter yesterday news"""
    yesterday = get_ist_yesterday()
    return df[df["EXCHANGE DISSEMINATION TIME"].dt.date == yesterday]


def print_yesterday_news(df):
    """print yesterday news"""
    yesterday_df = filter_yesterday_news(df)

    if yesterday_df.empty:
        print("No NSE insider trading news for yesterday (IST).")
        return

    print(f"Found {len(yesterday_df)} news item(s) for yesterday:\n")

    for _, row in yesterday_df.iterrows():
        print(
            f"- SYMBOL: {row['SYMBOL']}\n"
            f"  COMPANY: {row['COMPANY NAME']}\n"
            f"  BROADCAST: {row['BROADCAST DATE/TIME']}\n"
            f"  DETAILS: {row['DETAILS']}\n"
        )

def generate_telegram_message(df):
    """Generate a beautiful Telegram-friendly message for NSE news."""

    yesterday_df = filter_yesterday_news(df)

    if yesterday_df.empty:
        return "📢 *NSE Insider Trading Update*\n\nNo news for yesterday (IST)."

    lines = []
    lines.append("📢 *NSE Insider Trading Update (Yesterday)*\n")

    for _, row in yesterday_df.iterrows():
        symbol = row["SYMBOL"]
        company = row["COMPANY NAME"]
        broadcast = row["BROADCAST DATE/TIME"].strftime("%d-%b-%Y %H:%M:%S")
        details = row["DETAILS"]

        block = (
            f"🔔 *SYMBOL:* {symbol}\n"
            f"🏢 *Company:* {company}\n"
            f"🕒 *Broadcast:* {broadcast}\n"
            f"📄 *Details:* {details}\n"
            "------------------------------------"
        )
        lines.append(block)

    return "\n".join(lines)

def main():
    """run the main fuction"""
    notifier = get_notifier()
    df_data = extract_news()
    message = generate_telegram_message(df_data)
    notifier.send_message(message)

