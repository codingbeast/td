"""/td/strategies/hommagenius/main.py"""
from td.strategies.base_strategy import BaseStrategy
from td.strategies.hommagenius.logic import buy_logic
from td.strategies.comman.logic import sell_logic
from td.strategies.hommagenius.utils import get_stock_data_for_candle
from td.core.logging.console_logger import log

class HommageniusStrategy(BaseStrategy):
    """_summary_

    Args:
        BaseStrategy (_type_): _description_

    Returns:
        _type_: _description_
    """
    @property
    def name(self):
        return "Hommagenius"
    # REQUIRED abstract method (wrapper)
    def get_stock_data(self):
        """get stock data wrapper"""
        return get_stock_data_for_candle(self)
    def calculate_position_size(self,):
        """calculation is not required since calcuated from already"""
        return 0
    def generate_signals(self):
        signals = []
        if not self.config.enabled:
            return []
        if not self._should_run_now():
            return []
        if self.current_action == "buy":
            log.info("Generating BUY signal...")
            signals.extend(
                buy_logic(self)
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
                buy_logic(self)
            )
            # Then SELL
            signals.extend(
                sell_logic(self)
            )
        elif self.current_action == "check":
            log_msg = """check logic is not required for Hommagenius strategy"""
            log.info(log_msg)
        log.info("Hommagenius strategy generating signals...")
        return signals
