from datetime import date, timedelta
import math
from typing import Dict, List, Optional

from jugaad_trader import Zerodha
from td.strategies.base_strategy import BaseStrategy


class GoldbeesStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.required_methods_implemented = True  # Just for tracking
        self.broker = None  # Will be set by order manager

    def generate_signals(self) -> List[Dict]:
        signals = []
        stock_data = self._get_stock_data()
        # Single BUY
        if self.current_action == 'buy':
            signals.append(self._create_buy_signal(
                symbol=self.config['ticker'],
                quantity=self.calculate_position_size(),
                run_before_time=self.config['run_before_time'],
                run_after_time=self.config['run_after_time'],
                run_on_days=self.config['run_on_days'],
                order_type=self.config['order_type'],
                variety=self.config['variety'],
                exchange=self.config['exchange'],
                enabled=self.config['enabled'],
                price=stock_data['close'] - self.config.get('reduce', 0),
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
            signals.append(self._create_buy_signal(
                symbol=self.config['ticker'],
                quantity=self.calculate_position_size(),
                run_before_time=self.config['run_before_time'],
                run_after_time=self.config['run_after_time'],
                run_on_days=self.config['run_on_days'],
                order_type=self.config['order_type'],
                variety=self.config['variety'],
                exchange=self.config['exchange'],
                enabled=self.config['enabled'],
                price=stock_data['close'] - self.config.get('reduce', 0),
                cancel_old_order=self.config['cancel_old_order']
            ))

        elif self.current_action == 'check':
            holding = self._get_holding() #get last price this will not work
            signals.append(self._create_buy_signal(
                symbol=self.config['ticker'],
                quantity=self.calculate_position_size(),
                run_before_time=self.config['run_before_time'],
                run_after_time=self.config['run_after_time'],
                run_on_days=self.config['run_on_days'],
                order_type=self.config['order_type'],
                variety=Zerodha.VARIETY_REGULAR,
                exchange=self.config['exchange'],
                enabled=self.config['enabled'],
                price=holding['last_price'],
                cancel_old_order=self.config['cancel_old_order']
            ))

        return signals

    def calculate_position_size(self):
        """Calculate position size based on configured amount"""
        stock_data = self._get_stock_data()
        price = stock_data['close'] - self.config.get('reduce', 0)
        if self.config.get('amount_strict', False):
            return math.floor(self.config['amount'] / price)
        return math.ceil(self.config['amount'] / price)

    def _get_stock_data(self):
        """Helper method to get required stock data"""
        today = date.today()
        df = self.data_client.get_data(
            broker=self.broker,
            symbol=self.config['ticker'],
            from_date=today - timedelta(days=10),
            to_date=today,
            series="EQ"
        )
        return {
            'close': df['CLOSE'].iloc[-1],
            'high': df['HIGH'].iloc[-1],
            'low': df['LOW'].iloc[-1],
            'date' : df['DATE'].iloc[-1]
        }

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
        return "GOLDBEES"

    def set_broker(self, broker):
        """Set broker instance"""
        self.broker = broker
