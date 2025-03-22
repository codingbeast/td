import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from jugaad_data.nse import stock_df
import json, os
from datetime import datetime, date, timedelta
import argparse
import math
from jugaad_trader import Zerodha
from algoconnectorhelper.telegram.message_sender import send_message
from algoconnectorhelper.zerodha.connect_zerodha import getKite
from mycolorlogger.mylogger import log
from crontab import CronTab
import subprocess
import pandas as pd
import getpass
from pathlib import Path
from typing import Dict
import sys
logger = log.logger

STOCK = {
    "ticker": "GOLDBEES",
    "stock": "GOLDBEES",
    "amount": 100,
    "reduce": 0.30,
    "ISBUY": True
}

class USER_SETUP:
    def __init__(self) -> None:
        super().__init__()  # Initialize USER_SETUP class
        self.TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', None)
        self.TELEGRAM_USER_ID = os.environ.get('TELEGRAM_USER_ID', None)
        self.ZERODHA_USER_ID = os.environ.get('ZERODHA_USER_ID', None)
        self.ZERODHA_USER_PASSWORD = os.environ.get('ZERODHA_USER_PASSWORD', None)
        self.ZERODHA_TPIN_TOKEN = os.environ.get('ZERODHA_TPIN_TOKEN', None)
        self.base_log_folder = self.get_log_folder()

    def get_log_folder(self):
        """Set log path dynamically for local and GitHub Actions"""
        if os.getenv('GITHUB_ACTIONS') == 'true':
            base_folder = os.getenv('GITHUB_WORKSPACE', '/home/runner/work')
            log_folder = os.path.join(base_folder, 'gold_log')
        else:
            log_folder = os.path.join(os.path.expanduser('~'), "gold_log")

        Path(log_folder).mkdir(parents=True, exist_ok=True)
        return log_folder

    @property
    def isSetupDone(self):
        return os.path.exists(self.base_log_folder)

    def startSetup(self):
        Path(self.base_log_folder).mkdir(parents=True, exist_ok=True)
        return True

    def getUser(self) -> Zerodha:
        kite = getKite(user_id=self.ZERODHA_USER_ID, password=self.ZERODHA_USER_PASSWORD, otp_secret_key=self.ZERODHA_TPIN_TOKEN)
        return kite

    def sendTelegramMessage(self, message) -> bool:
        send_message(self.TELEGRAM_TOKEN, self.TELEGRAM_USER_ID, message)
        return True

    def main(self):
        parser = argparse.ArgumentParser(description='Script to perform buy or sell operation')
        parser.add_argument('--buy', action='store_true', help='Perform buy operation')
        parser.add_argument('--sell', action='store_true', help='Perform sell operation')
        parser.add_argument("--check", action='store_true', help='Check if stock is in position')
        parser.add_argument('--schedule-buy', action='store_true', help='Schedule buy operation')
        parser.add_argument('--schedule-sell', action='store_true', help='Schedule sell operation')
        parser.add_argument('--remove-job', action='store_true', help='Remove all cron jobs')
        args = parser.parse_args()

        if args.buy:
            return "buy"
        elif args.sell:
            return "sell"
        elif args.schedule_buy:
            return "sbuy"
        elif args.schedule_sell:
            return "ssell"
        elif args.remove_job:
            return "remove"
        elif args.check:
            return "check"
        else:
            return False

    def logWriterOrder(self, productID, stock_code, isbuy):
        filename = os.path.join(self.base_log_folder, f'{stock_code}_{"buy" if isbuy else "sell"}.txt')
        with open(filename, 'w') as f:
            f.write(str(productID))
        return True

    def logWriterGtt(self, productID, stock_code, isbuy):
        filename = os.path.join(self.base_log_folder, f'{stock_code}_{"buy_gtt" if isbuy else "sell_gtt"}.txt')
        with open(filename, 'w') as f:
            f.write(str(productID))

    def cancelOrder(self, stock_code, kite: Zerodha, isbuy):
        filename = os.path.join(self.base_log_folder, f'{stock_code}_{"buy" if isbuy else "sell"}.txt')
        if not os.path.isfile(filename):
            return False
        with open(filename, 'r') as f:
            productID = f.read()
            gtt_order_id = int(productID)

        try:
            kite.cancel_order(order_id=gtt_order_id, variety=kite.VARIETY_AMO)
        except Exception:
            pass

        os.remove(filename)
        return True

    @property
    def getCurrentTime(self):
        current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        return current_datetime


class UTILITY:
    def __init__(self) -> None:
        self.base_log_folder = self.get_log_folder()

    def get_log_folder(self):
        if os.getenv('GITHUB_ACTIONS') == 'true':
            base_folder = os.getenv('GITHUB_WORKSPACE', '/home/runner/work')
            log_folder = os.path.join(base_folder, 'gold_log')
        else:
            log_folder = os.path.join(os.path.expanduser('~'), "gold_log")

        Path(log_folder).mkdir(parents=True, exist_ok=True)
        return log_folder

    def stockTodayClosePrice(self, stock):
        logger.info(f"Fetching data from -> {stock}")
        today = date.today()
        stock_data = stock_df(symbol=stock, from_date=today - timedelta(days=10),
            to_date=today, series="EQ")
        last_closing_price = stock_data['CLOSE'].iloc[0]
        return round(last_closing_price, 2)

    def calculateTotalShare(self, total_price, stock_price):
        return math.ceil(total_price / stock_price)

    def setCronjobBuy(self):
        cron = CronTab(user=True)
        cron.remove_all(comment='buy')
        job = cron.new(command=f'python3 {os.path.abspath(__file__)} --buy', comment='buy')
        job.setall('0 8 * * 1-5')  # Runs at 8 AM Mon-Fri
        cron.write()

    def setCronjobSell(self):
        cron = CronTab(user=True)
        cron.remove_all(comment='sell')
        job = cron.new(command=f'python3 {os.path.abspath(__file__)} --sell', comment='sell')
        job.setall('1 8 * * 1-5')  # Runs at 8:01 AM Mon-Fri
        cron.write()

    def deleteCronjobBuy(self):
        cron = CronTab(user=True)
        cron.remove_all(comment='buy')
        cron.write()

    def deleteCronjobSell(self):
        cron = CronTab(user=True)
        cron.remove_all(comment='sell')
        cron.write()


class GOLDBUY(UTILITY, USER_SETUP):
    def __init__(self) -> None:
        UTILITY.__init__(self)
        USER_SETUP.__init__(self)

    def placeBuyOrder(self, stock: Dict[str, any], kite: Zerodha) -> bool:
        stock_code = stock['stock']
        stock_current_price = self.stockTodayClosePrice(stock['ticker'])
        stock_buy_price = stock_current_price - stock['reduce']
        totalQuantity = self.calculateTotalShare(stock['amount'], stock_buy_price)

        if not stock['ISBUY']:
            logger.critical(f"Stock {stock_code} is ignored")
            return False

        self.cancelOrder(stock_code, kite, True)
        order_id = kite.place_order(
            tradingsymbol=stock_code,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=totalQuantity,
            variety=kite.VARIETY_AMO,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=stock_buy_price,
            disclosed_quantity = round(totalQuantity* 0.10)+1,
            product=kite.PRODUCT_CNC,
            validity=kite.VALIDITY_DAY
        )
        self.logWriterOrder(order_id, stock_code, True)
        self.sendTelegramMessage(f"Buy order placed for {stock_code} with order id {order_id} on {self.getCurrentTime}")
        return True


class GOLDSELL(UTILITY, USER_SETUP):
    def __init__(self) -> None:
        UTILITY.__init__(self)
        USER_SETUP.__init__(self)

    def placeSellOrder(self, stock: Dict[str, any], kite: Zerodha) -> bool:
        stock_code = stock['stock']
        holdings = kite.holdings()
        getgoldHolding = next((item for item in holdings if item['tradingsymbol'] == stock_code), None)
        if not getgoldHolding:
            logger.critical(f"No holdings found for {stock_code}")
            return False

        buyingPrice = float(getgoldHolding['average_price'])
        targetPrice = buyingPrice * 1.02
        totalQuantity = int(getgoldHolding['opening_quantity'])
        self.cancelOrder(stock_code, kite, False)
        order_id = kite.place_order(
            tradingsymbol=stock_code,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=totalQuantity,
            variety=kite.VARIETY_AMO,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=targetPrice,
            disclosed_quantity = round(totalQuantity* 0.10)+1,
            product=kite.PRODUCT_CNC,
            validity=kite.VALIDITY_DAY
        )
        self.logWriterOrder(order_id, stock_code, False)
        self.sendTelegramMessage(f"Sell order placed for {stock_code} with order id {order_id} on {self.getCurrentTime}")
        return True


if __name__ == "__main__":
    user_setup = USER_SETUP()
    flag = user_setup.main()
    kite = user_setup.getUser()

    if flag == "buy":
        goldbuy = GOLDBUY()
        goldbuy.placeBuyOrder(STOCK, kite)
    elif flag == "sell":
        goldsell = GOLDSELL()
        goldsell.placeSellOrder(STOCK, kite)
    elif flag == "sbuy":
        utility = UTILITY()
        utility.setCronjobBuy()
    elif flag == "ssell":
        utility = UTILITY()
        utility.setCronjobSell()
    elif flag == "remove":
        utility = UTILITY()
        utility.deleteCronjobBuy()
        utility.deleteCronjobSell()
    elif flag == "check":
        logger.info("Stock check option not implemented yet")
    else:
        logger.critical("Please add a valid flag when running")
        sys.exit(1)
