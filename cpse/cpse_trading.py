import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from jugaad_data.nse import stock_df
import json, os
from datetime import datetime, time,date, timedelta
import argparse
import math
from jugaad_trader import Zerodha
from algoconnectorhelper.telegram.message_sender import send_message
from algoconnectorhelper.zerodha.connect_zerodha import getKite
from mycolorlogger.mylogger import log
from datetime import datetime
from crontab import CronTab
import subprocess
import pandas as pd
import getpass
import argparse
from pathlib import Path
from typing import Dict
import math, sys
logger = log.logger


UPTRAND_PRICE = 8000
DOWNTRAND_PRICE = 10000

class FlagManager:
    def __init__(self, filename='flag.txt'):
        self.filename = filename
        self.initialize_file()

    def initialize_file(self):
        try:
            with open(self.filename, 'r') as file:
                pass
        except FileNotFoundError:
            # If the file does not exist, create it with 4 True values
            with open(self.filename, 'w') as file:
                file.write('True\nTrue\nTrue\nTrue\n')

    def check_flags(self):
        with open(self.filename, 'r') as file:
            flags = file.readlines()
        flags = [flag.strip() == 'True' for flag in flags]  # Convert to bool

        # Check if all flags are 'False'
        if all(flag == False for flag in flags):
            return False
        return True

    def update_flag(self, new_flag):
        with open(self.filename, 'r') as file:
            flags = file.readlines()
        flags = [flag.strip() == 'True' for flag in flags]  # Convert to bool

        # Remove the first flag and add the new flag to the end
        flags.pop(0)
        flags.append(new_flag)

        # Write the updated flags back to the file
        with open(self.filename, 'w') as file:
            for flag in flags:
                file.write(f"{str(flag)}\n")

class USER_SETUP:
    def __init__(self) -> None:
        super().__init__()  # Initialize USER_SETUP class to access its attributes
        # Token for accessing the Telegram Bot API
        self.TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN',None)
        # Another reference to the Telegram Bot token, if needed
        self.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN',None)
        # User ID for identifying the target user in Telegram
        self.TELEGRAM_USER_ID = os.environ.get('TELEGRAM_USER_ID',None)
        # User ID for accessing Zerodha trading account
        self.ZERODHA_USER_ID = os.environ.get('ZERODHA_USER_ID',None)
        # Password for accessing Zerodha trading account
        self.ZERODHA_USER_PASSWORD = os.environ.get('ZERODHA_USER_PASSWORD',None)
        # TPIN (Two-factor Personal Token) token for Zerodha authentication
        self.ZERODHA_TPIN_TOKEN = os.environ.get('ZERODHA_TPIN_TOKEN',None)
        # Directory containing the script
        self.script_dir = os.path.dirname(__file__)
        # Directory for storing the logs
        self.base_log_folder = os.path.join(os.path.expanduser('~'),"cpse_log")
        #self.base_log_folder = os.path.join(self.script_dir, 'log')
        Path(self.base_log_folder).mkdir(parents=True, exist_ok=True)
    @property
    def isSetupDone(self,):
        if os.path.exists(self.base_log_folder):
            return True
        return False
    
    def startSetup(self,):
        Path(self.base_log_folder).mkdir(parents=True, exist_ok=True)
        return True
    def getUser(self) -> Zerodha:
        # Get the Kite instance
        kite = getKite(user_id=self.ZERODHA_USER_ID, password=self.ZERODHA_USER_PASSWORD, otp_secret_key=self.ZERODHA_TPIN_TOKEN)
        return kite
    
    def sendTelegramMessage(self, message) -> bool:
        # send message to telegram about your buying/selling/etc.
        send_message(self.TELEGRAM_TOKEN, self.TELEGRAM_USER_ID, message)
        return True
    def main(self,):
        parser = argparse.ArgumentParser(description='Script to perform buy or sell operation')
        parser.add_argument('--buy', action='store_true', help='Perform buy operation')
        parser.add_argument('--sell', action='store_true', help='Perform sell operation')
        parser.add_argument("--check", action='store_true', help='check the stock already in position or not')
        parser.add_argument('--schedule-buy', action='store_true', help='schedule buy opration')
        parser.add_argument('--schedule-sell', action='store_true', help='schedule sell operation')
        parser.add_argument('--remove-job', action='store_true', help='remove all job  operation')
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
    def logWriterOrder(self,productID, stock_code,isbuy):
        if isbuy:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_buy.txt')
        else:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_sell.txt')
        with open(filename, 'w') as f:
            f.write(productID)
        return True
    
    def logWriterGtt(self, productID, stock_code, isbuy):
        if isbuy:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_buy_gtt.txt')
        else:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_sell_gtt.txt')
        with open(filename, 'w') as f:
            f.write(productID)

    def cancelOrder(self, stock_code, kite : Zerodha, isbuy):
        # Cancel the buy order for the given stock
        if isbuy:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_buy.txt')
        else:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_sell.txt')
        isFileAvailable = os.path.isfile(filename)
        if not isFileAvailable:
            return False
        with open(filename, 'r') as f:
            productID = f.read()
            gtt_order_id = int(productID)
        try:
            kite.cancel_order(order_id=gtt_order_id, variety= kite.VARIETY_AMO)
        except:
            pass
        os.remove(filename)
        return True
    def cancelGttOrder(self, stock_code, kite, isbuy):
        if isbuy:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_buy_gtt.txt')
        else:
            filename = os.path.join(self.base_log_folder, f'{stock_code}_sell_gtt.txt')
        isFileAvailable = os.path.isfile(filename)
        if not isFileAvailable:
            return False
        with open(filename, 'r') as f:
            productID = f.read()
            gtt_order_id = int(productID)
        # Cancel the buy order for the given stock
        try:
            kite.cancel_gtt(gtt_id=gtt_order_id)
        except:
            pass
        os.remove(filename)
        return True
    @property
    def getCurrentTime(self,):
        current_datetime = datetime.now()
        # Format the date and time as dd:mm:yyyy hh:mm:ss
        formatted_datetime = current_datetime.strftime("%d:%m:%Y %H:%M:%S")
        return formatted_datetime

class UTILITY:
    def __init__(self) -> None:
        self.current_user = getpass.getuser()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__()  # Initialize USER_SETUP class to access its attributes
        
    @property
    def getConfig(self,) -> dict:
        configPath = os.path.join(self.current_dir,'config.json')
        if os.path.exists(configPath):
            with open(configPath) as f:
                config = json.load(f)
                return config
        else:
            return {
                "STOCK_CODE" : "CPSEETF.NS",
                "ZERODHA_CODE_NSE" : "CPSEETF" 
            }
            
    def getPricesData(self,limitPrices : list , new_total) -> list:
        current_total = sum(limitPrices)
        scaling_factor = new_total / current_total
        adjusted_prices = [price * scaling_factor for price in limitPrices]
        adjusted_prices = [round(i) for i in adjusted_prices]
        return adjusted_prices
    
    def genUp(self, price, flag : bool) -> list:
        limitPrices = [1000, 500, 400, 300, 400, 500, 600, 700 ]
        limitPrices = self.getPricesData(limitPrices = limitPrices, new_total=UPTRAND_PRICE)
        finalPrices = [price-0.3,  price - 0.6, price - 0.9, price - 1.2, price - 1.5, price - 1.8, price - 2.1, price - 2.4 ]
        temp = []
        for i,j in zip(limitPrices, finalPrices):
            qnt = self.calculate_total_shares(i,j)
            temp.append({
                "PRICE" : round(j, 2),
                "QNT" : qnt,
                "STOCK CODE" : self.getConfig['ZERODHA_CODE_NSE'],
                "ISBUY" : True,
                "isUpTrand" : flag
            })
        return temp
    def genDown(self, price, flag : bool) -> list:
        limitPrices = [50, 300, 400, 500, 600, 700, 800, 900 ]
        limitPrices = self.getPricesData(limitPrices = limitPrices, new_total=DOWNTRAND_PRICE)
        finalPrices = [price - 0.3, price - 0.7, price - 1.4, price - 2.1, price - 2.8, price - 3.5, price - 4.2, price - 4.9]
        temp = []
        for i,j in zip(limitPrices, finalPrices):
            qnt = self.calculate_total_shares(i,j)
            temp.append({
                "PRICE" : round(j, 2),
                "QNT" : qnt,
                "STOCK CODE" : self.getConfig['ZERODHA_CODE_NSE'],
                "ISBUY" : True,
                "isUpTrand" : flag
            })
        return temp
    @property
    def getStockData(self) -> list[dict[str, any]]:
        configdata = self.getConfig
        today = date.today()
        df = stock_df(symbol=configdata['ZERODHA_CODE_NSE'], from_date=today - timedelta(days=30),
            to_date=today, series="EQ")
        df.sort_values(by='DATE', ascending=True, inplace=True)
        last_15_rows = df.tail(15)
        historydata = [round(i,2) for i in list(last_15_rows['CLOSE'])]
        avgPrice = historydata[-1]
        avgPrice2 = sum(historydata[-2:])/2
        avgPrice3 = sum(historydata[-3:])/3
        avgPrice4 = sum(historydata[-4:])/4
        avgPrice5 = sum(historydata[-5:])/5
        finalAvg = round(sum([avgPrice2, avgPrice3, avgPrice4, avgPrice5])/4,2)
        isUPTrand = True if avgPrice>finalAvg else False
        logger.info(f"market isUPTRAND : {isUPTrand}")
        logger.info(f"current Price : {avgPrice}")
        logger.info(f"uptrand Price : {finalAvg}")
        if isUPTrand:
            stockdata = self.genUp(price=avgPrice, flag=isUPTrand)
        else:
            stockdata = self.genDown(price=avgPrice, flag = isUPTrand)
        return stockdata
    def calculate_total_shares(self, total_price, stock_price):
        total_shares = math.ceil(total_price / stock_price)  # Round the result to the nearest integer
        return total_shares
    
    def setCronjobBuy(self,):
        #self.deleteCronjobBuy()
        #cron = CronTab(user=True)
        current_script_path = os.path.abspath(__file__)
        filename = "buy.sh"
        shdata = f"""#!/bin/bash
/usr/bin/python3 {current_script_path} --buy"""
        with open(filename, 'w') as f:
            f.write(shdata)
        command = os.path.join(self.current_dir, filename)
        logger.info("add this command in the crontab")
        print(command)
        subprocess.run(['chmod', '+x', command])
        #job = cron.new(command=command)
        #job.minute.on(0)
        #job.hour.on(8)
        #cron.write()
        
    def setCronjobSell(self,):
        #self.deleteCronjobSell()
        #cron = CronTab(user=True)
        current_script_path = os.path.abspath(__file__)
        filename = "sell.sh"
        shdata = f"""#!/bin/bash
/usr/bin/python3 {current_script_path} --sell"""
        with open(filename, 'w') as f:
            f.write(shdata)
        command = os.path.join(self.current_dir, filename)
        subprocess.run(['chmod', '+x', command])
        logger.info("add this command in the crontab")
        print(command)
        #job = cron.new(command=command)
        #job.minute.on(1)
        #job.hour.on(8)
        #cron.write()
    def deleteCronjobBuy(self,):
        cron = CronTab(user=True)
        command1 = os.path.join(self.current_dir, 'buy.sh')
        for job in cron:
            # Check if the command of the cron job matches the one you want to remove
            if job.command == command1:
                # Remove the cron job
                cron.remove(job)
        cron.write()
    def deleteCronjobSell(self,):
        cron = CronTab(user=True)
        command2 = os.path.join(self.current_dir, 'sell.sh')
        for job in cron:
            # Check if the command of the cron job matches the one you want to remove
            if job.command == command2:
                # Remove the cron job
                cron.remove(job)
        cron.write()

class CPSEBUY(UTILITY, USER_SETUP):
    def __init__(self) -> None:
        super().__init__()  # Initialize USER_SETUP class to access its attributes
    def placeBuyOrder(self, stock: Dict[str, any], kite  : Zerodha) -> bool:
        stock_code = stock['STOCK CODE'].split(":")[-1].strip()
        stock_BuyPrice = stock['PRICE']
        totalQuantity =  stock['QNT']
        buyFlag = bool(stock['ISBUY'])
        if not buyFlag:
            logger.critical(f"stock code {stock_code} is  ignored")
            return False
        #self.cancelOrder(stock_code, kite, True)
        order_id =kite.place_order(tradingsymbol=stock_code,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=totalQuantity,
            variety=kite.VARIETY_AMO,
            order_type=kite.ORDER_TYPE_LIMIT,
            price = stock_BuyPrice,
            product=kite.PRODUCT_CNC,
            disclosed_quantity = round(totalQuantity* 0.10)+1,
            validity=kite.VALIDITY_DAY)
        self.logWriterOrder(order_id, stock_code, True)
        self.sendTelegramMessage(f"Buy order placed for {stock_code} with order id {order_id} date : {self.getCurrentTime}")
class CPSESELL(UTILITY, USER_SETUP):
    def __init__(self) -> None:
        super().__init__()  # Initialize USER_SETUP class to access its attributes
    def placeSellOrder(self, stock: Dict[str, any], kite  : Zerodha) -> bool:
        # Place sell order for the given stock
        stock_code = stock['STOCK CODE'].split(":")[-1].strip()
        #stock_code = "CPSEETF"
        holdings = kite.holdings()
        getgoldHolding = next((item for item in holdings if item['tradingsymbol'] == stock_code), None)
        if getgoldHolding is None:
            logger.critical(f"stock code {stock_code} is  ignored")
            return False
        buyingPrice = float(getgoldHolding['average_price'])
        targetPrice = buyingPrice * 1.03
        totalQuantity = int(getgoldHolding['opening_quantity'])
        self.cancelOrder(stock_code, kite, False)
        order_id =kite.place_order(tradingsymbol=stock_code,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=totalQuantity,
            variety=kite.VARIETY_AMO,
            order_type=kite.ORDER_TYPE_LIMIT,
            price = targetPrice,
            product=kite.PRODUCT_CNC,
            disclosed_quantity = round(totalQuantity* 0.10)+1,
            validity=kite.VALIDITY_DAY)
        self.logWriterOrder(order_id, stock_code, False)
        self.sendTelegramMessage(f"Sell order placed for {stock_code} with order id {order_id} date : {self.getCurrentTime}")

class CPSECHECK(UTILITY, USER_SETUP):
    def __init__(self) -> None:
        super().__init__()  # Initialize USER_SETUP class to access its attributes
    def statusCheck(self,stock : Dict[str, any],  kite  : Zerodha):
        positions = kite.positions().get("net",{})
        for position in positions:
            if position["tradingsymbol"] == stock["STOCK CODE"]:
                logger.info(f"stock code {stock['STOCK CODE']} is already in positions")
                return False
        order_id = kite.place_order(tradingsymbol=stock["STOCK CODE"],
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=stock["QNT"],
            variety=kite.VARIETY_REGULAR,
            order_type=kite.ORDER_TYPE_MARKET,
            #price = stock["PRICE"],
            product=kite.PRODUCT_CNC,
            disclosed_quantity = round(stock["QNT"]* 0.10)+1,
            validity=kite.VALIDITY_DAY)
        self.sendTelegramMessage(f"Sell order placed for {stock['STOCK CODE']} with order id {order_id} date : {self.getCurrentTime}")
if __name__ == "__main__":
    user_setup = USER_SETUP()
    if not user_setup.isSetupDone:
        user_setup.startSetup()
    flag = user_setup.main()
    kite = user_setup.getUser()
    manager = FlagManager()
    if flag=="buy":
        cpsebuy = CPSEBUY()
        stocksdata = cpsebuy.getStockData
        is_flag_set = False
        for stock in stocksdata:
            if is_flag_set == False:
                manager.update_flag(stock['isUpTrand'])
                is_flag_set = True
            if (manager.check_flags() == False):
                continue
            cpsebuy.placeBuyOrder(stock, kite)
            #break
    elif flag=="sell":
        cpsesell = CPSESELL()
        stocksdata = cpsesell.getStockData
        for stock in stocksdata:
            cpsesell.placeSellOrder(stock, kite)
            break
    elif flag=="sbuy":
        utility = UTILITY()
        utility.setCronjobBuy()
        
    elif flag=="ssell":
        utility = UTILITY()
        utility.setCronjobSell()
    elif flag=="remove":
        utility = UTILITY()
        utility.deleteCronjobBuy()
        utility.deleteCronjobSell()
    elif flag=="check":
        check = CPSECHECK()
        cpsebuy = CPSEBUY()
        stocksdata = cpsebuy.getStockData
        for stock in stocksdata:
            check.statusCheck(stock, kite)
            break

    else:
        logger.critical("please add flag when run")
        exit()
    
