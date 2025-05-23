from datetime import date, timedelta
import math
from typing import Dict, List, Optional

from jugaad_trader import Zerodha
from td.strategies.base_strategy import BaseStrategy
from td.core.logging.google_drive import FlagManager
from mycolorlogger.mylogger import log

message_logger = log.logger

class CpseStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.required_methods_implemented = True  # Just for tracking
        self.broker = None  # Will be set by order manager

    def generate_signals(self) -> List[Dict]:
        signals = []
        stock_data = self._get_stock_data()
        manager = FlagManager()
        is_flag_set = False
        if self.current_action == 'buy':
            #buy order run 
            for stock in stock_data:
                if is_flag_set == False:
                    manager.update_flag(stock['isUpTrand'])
                    is_flag_set = True
                if (manager.check_flags() == False):
                    continue
                signals.append(self._create_buy_signal(
                    symbol=self.config['ticker'],
                    quantity=stock['QNT'],
                    run_before_time=self.config['run_before_time'],
                    run_after_time=self.config['run_after_time'],
                    run_on_days=self.config['run_on_days'],
                    order_type=self.config['order_type'],
                    variety=self.config['variety'],
                    exchange=self.config['exchange'],
                    price=stock['PRICE'],
                    enabled=self.config['enabled'],
                    cancel_old_order=self.config['cancel_old_order']
                ))
        elif self.current_action == 'sell':
            #sell order run
            if holding := self._get_holding():
                sell_price = max(
                    holding['average_price'] * self.config.get("profit_percentage", 1.03),
                    holding['last_price']
                )
                sell_qnt = holding['quantity']
                sell_qnt = sell_qnt if self.config.get("min_sell_qnt") < sell_qnt else 0
                signals.append(self._create_sell_signal(
                    symbol=self.config['ticker'],
                    quantity=sell_qnt,
                    run_before_time=self.config['run_before_time'],
                    run_after_time=self.config['run_after_time'],
                    run_on_days=self.config['run_on_days'],
                    order_type=self.config['order_type'],
                    variety=self.config['variety'],
                    exchange=self.config['exchange'],
                    price=sell_price,
                    enabled=self.config['enabled'],
                    cancel_old_order=self.config['cancel_old_order']
                ))
        elif self.current_action == 'buy-sell':
            for stock in stock_data:
                if is_flag_set == False:
                    manager.update_flag(stock['isUpTrand'])
                    is_flag_set = True
                if (manager.check_flags() == False):
                    continue
                signals.append(self._create_buy_signal(
                    symbol=self.config['ticker'],
                    quantity=stock['QNT'],
                    run_before_time=self.config['run_before_time'],
                    run_after_time=self.config['run_after_time'],
                    run_on_days=self.config['run_on_days'],
                    order_type=self.config['order_type'],
                    variety=self.config['variety'],
                    exchange=self.config['exchange'],
                    price=stock['PRICE'],
                    enabled=self.config['enabled'],
                    cancel_old_order=self.config['cancel_old_order']
                ))
            if holding := self._get_holding():
                sell_price = max(
                    holding['average_price'] * self.config.get("profit_percentage", 1.03),
                    holding['last_price']
                )
                sell_qnt = holding['quantity']
                sell_qnt = sell_qnt if self.config.get("min_sell_qnt") < sell_qnt else 0
                signals.append(self._create_sell_signal(
                    symbol=self.config['ticker'],
                    quantity=sell_qnt,
                    run_before_time=self.config['run_before_time'],
                    run_after_time=self.config['run_after_time'],
                    run_on_days=self.config['run_on_days'],
                    order_type=self.config['order_type'],
                    variety=self.config['variety'],
                    exchange=self.config['exchange'],
                    price=sell_price,
                    enabled=self.config['enabled'],
                    cancel_old_order=self.config['cancel_old_order']
                ))
        elif self.current_action == 'check':
            if position := self._get_position():
                if position == False:
                    for stock in stock_data:
                        signals.append(self._create_buy_signal(
                            symbol=self.config['ticker'],
                            quantity=stock['QNT'],
                            run_before_time=self.config['run_before_time'],
                            run_after_time=self.config['run_after_time'],
                            run_on_days=self.config['run_on_days'],
                            order_type=self.config['order_type'],
                            variety=Zerodha.VARIETY_REGULAR,
                            exchange=self.config['exchange'],
                            enabled=self.config['enabled'],
                            price=stock['PRICE'],
                            cancel_old_order=self.config['cancel_old_order']
                        ))
                        break #only single order should place on check point
        return signals
    
    def calculate_position_size(self):
        """Calculate position size based on configured amount"""
        stock_data = self._get_stock_data()
        price = stock_data['close'] - self.config.get('reduce', 0)
        if self.config.get('amount_strict', False):
            return math.floor(self.config['amount'] / price)
        return math.ceil(self.config['amount'] / price)
    def calculate_total_shares(self, total_price, stock_price):
        if self.config.get('amount_strict', False):
            return math.floor(total_price / stock_price)
        return math.ceil(total_price / stock_price)  # Round the result to the nearest integer
    def _get_stock_data(self):
        """Helper method to get required stock data"""
        today = date.today()
        df = self.data_client.get_data(
            symbol=self.config['ticker'],
            from_date=today - timedelta(days=30),
            to_date=today,
            series="EQ"
        )
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
        message_logger.info(f"market isUPTRAND : {isUPTrand}")
        message_logger.info(f"current Price : {avgPrice}")
        message_logger.info(f"uptrand Price : {finalAvg}")
        if isUPTrand:
            stockdata = self.genUp(price=avgPrice, flag=isUPTrand)
        else:
            stockdata = self.genDown(price=avgPrice, flag = isUPTrand)
        return stockdata
    
    def genUp(self, price, flag : bool) -> list:
        limitPrices = [200, 500, 400, 300, 400, 500, 600, 700 ]
        limitPrices = self.getPricesData(limitPrices = limitPrices, new_total=self.config.get('uptrand_price'))
        finalPrices = [price-0.3,  price - 0.6, price - 0.9, price - 1.2, price - 1.5, price - 1.8, price - 2.1, price - 2.4 ]
        temp = []
        for i,j in zip(limitPrices, finalPrices):
            qnt = self.calculate_total_shares(i,j)
            temp.append({
                "PRICE" : round(j, 2),
                "QNT" : qnt,
                "isUpTrand" : flag
            })
        return temp
    def genDown(self, price, flag : bool) -> list:
        limitPrices = [50, 300, 400, 500, 600, 700, 800, 900 ]
        limitPrices = self.getPricesData(limitPrices = limitPrices, new_total=self.config.get('downtrand_price'))
        finalPrices = [price - 0.3, price - 0.7, price - 1.4, price - 2.1, price - 2.8, price - 3.5, price - 4.2, price - 4.9]
        temp = []
        for i,j in zip(limitPrices, finalPrices):
            qnt = self.calculate_total_shares(i,j)
            temp.append({
                "PRICE" : round(j, 2),
                "QNT" : qnt,
                "isUpTrand" : flag
            })
        return temp
    def getPricesData(self,limitPrices : list , new_total) -> list:
        current_total = sum(limitPrices)
        scaling_factor = new_total / current_total
        adjusted_prices = [price * scaling_factor for price in limitPrices]
        adjusted_prices = [round(i) for i in adjusted_prices]
        return adjusted_prices
    def _get_holding(self) -> Optional[Dict]:
        """Get current holding for the symbol"""
        if self.broker is not None:
            holdings = self.broker.get_holdings()
            return next(
                (h for h in holdings if h['tradingsymbol'] == self.config['ticker']),
                None
            )
        return None
    def _get_position(self,) -> Optional[bool]:
        """"get current position for the symbol"""
        if self.broker is not None:
            positions = self.broker.get_positions().get("net",{})
            for position in positions:
                if position["tradingsymbol"] == self.config['ticker']:
                    message_logger.info(f"stock code {self.config['ticker']} is already in positions")
                    return False
            return True
        return None
    @property
    def name(self):
        """Return strategy name"""
        return "CPSE"

    def set_broker(self, broker):
        """Set broker instance"""
        self.broker = broker


