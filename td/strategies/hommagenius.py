from datetime import date, timedelta
import math
from typing import Dict, List, Optional

from jugaad_trader import Zerodha
from td.strategies.base_strategy import BaseStrategy
from td.core.logging.google_drive import FlagManager
from mycolorlogger.mylogger import log

message_logger = log.logger


class HommaGeniusStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.required_methods_implemented = True  # Just for tracking
        self.broker = None  # Will be set by order manager

    def generate_signals(self) -> List[Dict]:
        signals = []
        stock_data = self._get_stock_data()
        # Single BUY
        if self.current_action == 'buy':
            pass
        # Single SELL
        elif self.current_action == 'sell':
            pass

        # BUY-SELL combo
        elif self.current_action == 'buy-sell':
            pass
        elif self.current_action == 'check':
            pass
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
