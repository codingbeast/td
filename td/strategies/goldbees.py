from td.strategies.base_strategy import BaseStrategy
from datetime import date, timedelta
import math

# td/strategies/goldbees.py
from td.strategies.base_strategy import BaseStrategy
import math

class GoldbeesStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.required_methods_implemented = True  # Just for tracking
        self.broker = None  # Will be set by order manager
    
    def generate_signals(self):
        """Generate trading signals for GOLDBEES"""
        signals = []
        stock_data = self._get_stock_data()
        if self.current_action == 'buy' or (self.current_action != 'sell' and self.current_action != 'buy-sell' and self.config.get('ISBUY', False)):
            signals.append({
                'action': 'BUY',
                'symbol': self.config['ticker'],
                'quantity': self.calculate_position_size(),
                'price': stock_data['close'] - self.config.get('reduce', 0),
                'order_type': 'LIMIT'
            })
        elif self.current_action == 'sell':
            # Add your sell logic here
            holdings = self.broker.get_holdings()
            gold_holding = next((h for h in holdings if h['tradingsymbol'] == self.config['ticker']), None)
            if gold_holding and gold_holding['quantity'] >= self.config['min_sell_qnt']:
                signals.append({
                    'action': 'SELL',
                    'symbol': self.config['ticker'],
                    'quantity': gold_holding['quantity'],
                    'price': gold_holding['average_price'] * 1.02,  # 2% above average
                    'order_type': 'LIMIT'
                })
        elif self.current_action == 'buy-sell':
            # Add your sell logic here
            holdings = self.broker.get_holdings()
            gold_holding = next((h for h in holdings if h['tradingsymbol'] == self.config['ticker']), None)
            if gold_holding and gold_holding['quantity'] >= self.config['min_sell_qnt']:
                sell_qnt = gold_holding['quantity']
            else:
                sell_qnt = 0
            signals.append({
                'action': 'BUY-SELL',
                'symbol': self.config['ticker'],
                'sell_quantity': sell_qnt,
                'sell_price': gold_holding['average_price'] * 1.02,  # 2% above average
                'buy_quantity': self.calculate_position_size(),
                'buy_price': stock_data['close'] - self.config.get('reduce', 0),
                'order_type': 'LIMIT'
            })
        return signals
    
    def calculate_position_size(self):
        """Calculate position size based on configured amount"""
        stock_data = self._get_stock_data()
        price = stock_data['close'] - self.config.get('reduce', 0)
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
            'close': df['CLOSE'].iloc[0],
            'high': df['HIGH'].iloc[0],
            'low': df['LOW'].iloc[0]
        }
    
    @property
    def name(self):
        return "GOLDBEES"
    def set_broker(self, broker):
        self.broker = broker