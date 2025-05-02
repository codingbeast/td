from datetime import date, timedelta
import math
from typing import Dict, List, Optional

from jugaad_trader import Zerodha
from td.strategies.base_strategy import BaseStrategy



class CpseStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.required_methods_implemented = True  # Just for tracking
        self.broker = None  # Will be set by order manager

    def generate_signals(self) -> List[Dict]:
        signals = []
        stock_data = self._get_stock_data()
        if self.current_action == 'buy':
            pass
        elif self.current_action == 'sell':
            pass
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

    @property
    def name(self):
        """Return strategy name"""
        return "CPSE"

    def set_broker(self, broker):
        """Set broker instance"""
        self.broker = broker
