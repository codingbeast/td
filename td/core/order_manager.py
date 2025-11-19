""""Order Manager Module"""
# pylint: disable=broad-exception-caught
from datetime import datetime
from math import ceil
from td.config.models_config.common_enums import Variety
from td.core.logging.console_logger import log


class OrderManager:
    """_summary_
    """
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"
    def __init__(self, broker, drive_logger, message_logger, notifier):
        self.broker = broker
        self.drive_logger = drive_logger
        self.message_logger = message_logger
        self.notifier = notifier
    def execute_strategy_orders(self, strategy):
        """Execute buy/sell orders based on strategy signals"""
        strategy.set_broker(self.broker)
        signals = strategy.generate_signals()
        for signal in signals:
            action = signal["action"].upper()
            if action=='BUY-SELL':
                self._execute_sell(signal)
                self._execute_buy(signal)
            elif action == 'BUY':
                self._execute_buy(signal)
            elif action == 'SELL':
                self._execute_sell(signal)
            elif signal['action'] == 'CHECK':
                self._execute_check(signal)
                print("------ CHECK signal ------------------")
    def _generate_order_params(self, signal, is_check : bool = False):
        min_disclosed = ceil(signal['quantity'] * 0.1)
        # Convert variety (Enum or str) → CLEAN string
        variety = signal['variety']
        if hasattr(variety, "value"):
            variety = variety.value  # Enum → string

        # Force regular variety only for check orders
        if is_check:
            variety = Variety.REGULAR.value
        return {
            'tradingsymbol': signal['symbol'],
            'exchange': signal['exchange'],
            'transaction_type': signal['action'],
            'quantity': signal['quantity'],
            'variety': variety,
            'order_type': signal['order_type'],
            'price': round(float(signal['price']), 2),
            'product': signal['product_type'],
            'validity': signal['validity'],
            'disclosed_quantity': min(signal['quantity'] - 1, min_disclosed)
                if signal['quantity'] > 1 else 0
        }
    def _execute_buy(self, signal):
        """this is run when buy signal is generated"""
        try:
            log.info("Attempting BUY order for %s", signal['symbol'])
            if signal['cancel_old_order']:
                self.log_cancel_order(signal['strategy'], signal['variety'], True)
            order_params = self._generate_order_params(signal)
            order_id = self.broker.place_order(**order_params)
            if signal['cancel_old_order']:
                self.log_writer_order(order_id, signal['strategy'], True)
            message = (f"[{signal['strategy']}]: BUY order placed - ID: {order_id} | "
                       f"{signal['quantity']} shares of {signal['symbol']} @ {signal['price']}")
            log.info(message)
            self.notifier.send_message(message)
            return {'status': 'SUCCESS', 'order_id': order_id, 'details': order_params}
        except Exception as e:
            error_msg = f"[{signal['strategy']}]: Failed BUY order for {signal['symbol']}: {str(e)}"
            log.error(error_msg)
            self.notifier.send_message(error_msg)
            return {'status': 'FAILED', 'error': error_msg, 'details': signal}
    def _execute_sell(self, signal):
        """this is run when sell signal is generated"""
        try:
            log.info("Attempting SELL order for %s", signal['symbol'])
            if signal['cancel_old_order']:
                self.log_cancel_order(signal['symbol'], signal['variety'], False)
            order_params = self._generate_order_params(signal)
            order_id = self.broker.place_order(**order_params)
            if signal['cancel_old_order']:
                self.log_writer_order(order_id, signal['strategy'], False)
            message = (f"[{signal['strategy']}]: SELL order placed - ID: {order_id} | "
                       f"{signal['quantity']} shares of {signal['symbol']} @ {signal['price']}")
            log.info(message)
            self.notifier.send_message(message)
            return {'status': 'SUCCESS', 'order_id': order_id, 'details': order_params}
        except Exception as e:
            error_msg = f"[{signal['strategy']}]: \
                Failed SELL order for {signal['symbol']}: {str(e)}"
            log.error(error_msg)
            self.notifier.send_message(error_msg)
            return {'status': 'FAILED', 'error': error_msg, 'details': signal}
    def _execute_check(self, signal):
        """this is run when buy signal is generated""" 
    def log_writer_order(self, product_id, strategy, is_buy):
        """log order to google drive"""
        filename = f'{strategy}_{"buy" if is_buy else "sell"}.txt'
        self.drive_logger.write_file(filename, str(product_id))
        return True

    def log_writer_gtt(self, product_id, strategy, is_buy):
        """log gtt order to google drive"""
        filename = f'{strategy}_{"buy_gtt" if is_buy else "sell_gtt"}.txt'
        self.drive_logger.write_file(filename, str(product_id))

    def log_cancel_order(self, strategy, variety: str, is_buy):
        """cancel old order if exists"""
        filename = f'{strategy}_{"buy" if is_buy else "sell"}.txt'
        if not self.drive_logger.file_exists(filename):
            return False
        product_id = self.drive_logger.read_file(filename)
        try:
            self.broker.cancel_order(
                order_id=int(product_id),
                variety=variety,
            )
        except Exception as e:
            log.error("Error cancelling order %s: %s", strategy, e)
        self.drive_logger.delete_file(filename)
        return True
    @property
    def get_current_time(self):
        """get current time and date"""
        return datetime.now().strftime(self.DATETIME_FORMAT)
