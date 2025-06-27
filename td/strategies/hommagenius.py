from datetime import date, datetime, timedelta
import math
from typing import Dict, List, Optional
from jugaad_trader import Zerodha
from td.strategies.base_strategy import BaseStrategy
from td.core.logging.google_drive import FlagManager
from mycolorlogger.mylogger import log

message_logger = log.logger


class HommageniusStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.required_methods_implemented = True  # Just for tracking
        self.broker = None  # Will be set by order manager

    def generate_signals(self) -> List[Dict]:
        signals = []
        stock_data = self._get_stock_data()
        # Single BUY
        if self.current_action == 'buy':
            if stock_data['isBearish'] == True:
                signals.append(self._create_buy_signal(
                    symbol=self.config['ticker'],
                    quantity=stock_data['qnt'],
                    run_before_time=self.config['run_before_time'],
                    run_after_time=self.config['run_after_time'],
                    is_time_between=self.config['is_time_between'],
                    run_on_days=self.config['run_on_days'],
                    order_type=self.config['order_type'],
                    variety=self.config['variety'],
                    exchange=self.config['exchange'],
                    enabled=self.config['enabled'],
                    price=stock_data['close_price'],
                    cancel_old_order=self.config['cancel_old_order']
                ))
        # Single SELL
        elif self.current_action == 'sell':
            if holding := self._get_holding():
                sell_price = max(
                    holding['average_price'] * self.config.get("profit_percentage", 1.02),
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

        # BUY-SELL combo
        elif self.current_action == 'buy-sell':
            if holding := self._get_holding():
                sell_price = max(
                    holding['average_price'] * self.config.get("profit_percentage", 1.02),
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
            if stock_data['isBearish'] == True:
                signals.append(self._create_buy_signal(
                    symbol=self.config['ticker'],
                    quantity=stock_data['qnt'],
                    run_before_time=self.config['run_before_time'],
                    run_after_time=self.config['run_after_time'],
                    run_on_days=self.config['run_on_days'],
                    order_type=self.config['order_type'],
                    variety=self.config['variety'],
                    exchange=self.config['exchange'],
                    enabled=self.config['enabled'],
                    price=stock_data['close_price'],
                    cancel_old_order=self.config['cancel_old_order']
                ))
        elif self.current_action == 'check':
                if stock_data['isBearish'] == True:
                    signals.append(self._create_buy_signal(
                        symbol=self.config['ticker'],
                        quantity=stock_data['qnt'],
                        run_before_time=self.config['run_before_time'],
                        run_after_time=self.config['run_after_time'],
                        run_on_days=self.config['run_on_days'],
                        order_type=self.config['order_type'],
                        variety=self.config['variety'],
                        exchange=self.config['exchange'],
                        enabled=self.config['enabled'],
                        price=stock_data['close_price'],
                        cancel_old_order=self.config['cancel_old_order']
                    ))
        return signals

    def calculate_position_size(self, stock_price):
        """Calculate position size based on configured amount"""
        if self.config.get('amount_strict', False):
            return math.floor(self.config['amount'] / stock_price)
        return math.ceil(self.config['amount'] / stock_price)
    def get_previous_week_range(self,):
        today = datetime.today()
        previous_friday = today - timedelta(days=6)
        adjusted_end_date = today + timedelta(days=1)
        return previous_friday.date(), adjusted_end_date.date()
    def check_candle_type(self, open_price, close_price):
        if close_price > open_price:
            return  False
        elif close_price < open_price:
            return True
        else:
            return True
    def _get_stock_data(self):
        """Helper method to get required stock data"""
        start_of_week, end_of_week = self.get_previous_week_range()
        df = self.data_client.get_data(
            broker=self.broker,
            symbol=self.config['ticker'],
            from_date=start_of_week,
            to_date=end_of_week,
            series="EQ"
        )
        stock ={}
        open_price = df.iloc[0]['OPEN']
        close_price = df.iloc[-1]['CLOSE']
        high_price = max(df['HIGH'])
        low_price = min(df['LOW'])
        stock['open_price']  = open_price
        stock['close_price'] = close_price
        stock['high_price']  = high_price
        stock['low_price']   = low_price
        stock['qnt'] = self.calculate_position_size(stock_price=close_price)
        stock['isBearish'] = self.check_candle_type(open_price=open_price, close_price=close_price)
        return stock

    def _get_holding(self) -> Optional[Dict]:
        """Get current holding for the symbol"""
        if self.broker is not None:
            holdings = self.broker.get_holdings()
            return next(
                (h for h in holdings if h['tradingsymbol'] == self.config['ticker']),
                None
            )
        return None

    @property
    def name(self):
        """Return strategy name"""
        return "HOMMAGENIUS"

    def set_broker(self, broker):
        """Set broker instance"""
        self.broker = broker
