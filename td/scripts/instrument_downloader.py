"""td/scripts/instrument_downloader.py"""
# pylint: disable=broad-exception-caught
import argparse
from io import StringIO
from pathlib import Path
import requests
import pandas as pd
from td.core.logging.console_logger import log


def fetch_and_filter_instruments(save_path: Path):
    """Download, filter, and save Zerodha EQ instruments."""
    url = "https://api.kite.trade/instruments"

    log.info("Downloading instruments from Zerodha...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        log.error("Failed to download: %s", e)
        raise

    # Convert CSV → DataFrame
    df = pd.read_csv(StringIO(response.text))

    # Select main columns
    df = df[
        [
            "instrument_token",
            "exchange_token",
            "tradingsymbol",
            "name",
            "instrument_type",
            "segment",
            "exchange",
        ]
    ]

    # Filter EQ + valid names
    df = df[
        (df["instrument_type"] == "EQ")
        & (df["name"].notna())
        & (df["name"].str.strip() != "")
    ]

    df.reset_index(drop=True, inplace=True)

    # Save file
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)

    log.info("Saved %s instruments to %s", len(df), save_path)


def main():
    """_summary_"""
    parser = argparse.ArgumentParser(
        description="Download & filter Zerodha instruments"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Fetch and save EQ instruments",
    )
    parser.add_argument(
        "--path",
        type=str,
        default="td/core/data/nse_instrument_token.csv",
        help="Where to save the CSV file",
    )

    args = parser.parse_args()

    if args.download:
        save_path = Path(args.path)
        fetch_and_filter_instruments(save_path)
    else:
        print("Use --download to fetch instruments.")


if __name__ == "__main__":
    main()
