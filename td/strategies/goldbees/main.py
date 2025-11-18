"""/td/strategies/goldbees/main.py"""
from td.strategies.base_strategy import BaseStrategy
from .logic import buy_logic, sell_logic
from .utils import position_size, get_stock_data, get_holding


class GoldbeesStrategy(BaseStrategy):
    """_summary_

    Args:
        BaseStrategy (_type_): _description_

    Returns:
        _type_: _description_
    """
    @property
    def name(self):
        return "Goldbees"

    # REQUIRED abstract method (wrapper)
    def calculate_position_size(self):
        stock = get_stock_data(self)
        return position_size(self, stock)

    # OPTIONAL but recommended wrapper:
    def _get_stock_data(self):
        return get_stock_data(self)

    def _get_holding(self):
        return get_holding(self)

    def generate_signals(self):
        signals = []
        if not self.config.enabled:
            return []
        if not self._should_run_now():
            return []
        if self.current_action == "buy":
            signals.extend(buy_logic(self))
        elif self.current_action == "sell":
            signals.extend(sell_logic(self))
        elif self.current_action == "buy-sell":
            # BUY first
            signals.extend(buy_logic(self))
            # Then SELL
            signals.extend(sell_logic(self))
        elif self.current_action == "check":
            #todo implement check logic
            pass

        return signals
