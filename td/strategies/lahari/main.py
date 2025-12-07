"""/td/strategies/hommagenius/main.py"""
from td.strategies.base_strategy import BaseStrategy
from td.strategies.comman.logic import sell_logic
from td.strategies.lahari.logic import buy_logic,check_logic
from td.core.logging.console_logger import log
from td.strategies.lahari.utils import get_stock_data

class LahariStrategy(BaseStrategy):
    """_summary_

    Args:
        BaseStrategy (_type_): _description_

    Returns:
        _type_: _description_
    """
    @property
    def name(self):
        return "Lahari"
    # REQUIRED abstract method (wrapper)
    def get_stock_data(self):
        """get stock data wrapper"""
        return get_stock_data(self)
    def calculate_position_size(self,):
        """calculation is not required since calcuated from already"""
        return 0
    def generate_signals(self):
        signals = []
        # if not self.config.enabled:
        #     return []
        # if not self._should_run_now():
        #     return []
        if self.current_action == "buy":
            log.info("Generating BUY signal...")
            signals.extend(
                buy_logic(self,get_stock_data)
            )
        elif self.current_action == "sell":
            log.info("Generating SELL signal...")
            signals.extend(
                sell_logic(self)
            )
        elif self.current_action == "buy-sell":
            log.info("Generating BUY-SELL signals...")
            # BUY first
            signals.extend(
                buy_logic(self,get_stock_data)
            )
            # Then SELL
            signals.extend(
                sell_logic(self)
            )
        elif self.current_action == "check":
            signals.extend(
                check_logic(self,get_stock_data)
            )
        log.info("Lahari strategy generating signals...")
        return signals
