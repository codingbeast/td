from math import ceil
from jugaad_trader import Zerodha
from datetime import datetime
import pytz


class OrderManager:
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
            if signal['action']=='BUY-SELL' and self._should_run(signal) and signal['enabled']==True:
                self._execute_sell(signal)
                self._execute_buy(signal)
            elif signal['action'] == 'BUY' and self._should_run(signal) and signal['enabled']==True:
                self._execute_buy(signal)
            elif signal['action'] == 'SELL' and self._should_run(signal) and signal['enabled']==True:
                self._execute_sell(signal)
            elif signal['action'] == 'CHECK' and self._should_run(signal) and signal['enabled']==True:
                #self._execute_buy(signal)
                # todo implement check
                print("------ CHECK signal ------------------")

    def _generate_order_params(self, signal, is_buy: bool):
        min_disclosed = ceil(signal['quantity'] * 0.1)
        return {
            'tradingsymbol': signal['symbol'],
            'exchange': signal['exchange'],
            'transaction_type': Zerodha.TRANSACTION_TYPE_BUY if is_buy else Zerodha.TRANSACTION_TYPE_SELL,
            'quantity': signal['quantity'],
            'variety': signal['variety'],
            'order_type': signal['order_type'],
            'price': round(float(signal['price']), 2),
            'product': signal['product_type'],
            'validity': Zerodha.VALIDITY_DAY,
            'disclosed_quantity': min(signal['quantity'] - 1, min_disclosed) if signal['quantity'] > 1 else 0
            
        }

    def _execute_buy(self, signal):
        try:
            self.message_logger.info(f"Attempting BUY order for {signal['symbol']}")
            if signal['cancel_old_order']:
                self.log_cancel_order(signal['symbol'], signal['variety'], True)
            order_params = self._generate_order_params(signal, is_buy=True)
            order_id = self.broker.place_order(**order_params)
            if signal['cancel_old_order']:
                self.log_writer_order(order_id, signal['symbol'], True)
            message = (f"BUY order placed - ID: {order_id} | "
                       f"{signal['quantity']} shares of {signal['symbol']} @ {signal['price']}")
            self.message_logger.info(message)
            self.notifier.send_message(message)

            return {'status': 'SUCCESS', 'order_id': order_id, 'details': order_params}
        except Exception as e:
            error_msg = f"Failed BUY order for {signal['symbol']}: {str(e)}"
            self.message_logger.error(error_msg)
            self.notifier.send_message(error_msg)
            return {'status': 'FAILED', 'error': error_msg, 'details': signal}

    def _execute_sell(self, signal):
        try:
            self.message_logger.info(f"Attempting SELL order for {signal['symbol']}")
            if signal['cancel_old_order']:
                self.log_cancel_order(signal['symbol'], signal['variety'], False)
            order_params = self._generate_order_params(signal, is_buy=False)
            order_id = self.broker.place_order(**order_params)
            if signal['cancel_old_order']:
                self.log_writer_order(order_id, signal['symbol'], False)

            message = (f"SELL order placed - ID: {order_id} | "
                       f"{signal['quantity']} shares of {signal['symbol']} @ {signal['price']}")
            self.message_logger.info(message)
            self.notifier.send_message(message)

            return {'status': 'SUCCESS', 'order_id': order_id, 'details': order_params}
        except Exception as e:
            error_msg = f"Failed SELL order for {signal['symbol']}: {str(e)}"
            self.message_logger.error(error_msg)
            self.notifier.send_message(error_msg)
            return {'status': 'FAILED', 'error': error_msg, 'details': signal}

    def log_writer_order(self, product_id, stock_code, is_buy):
        filename = f'{stock_code}_{"buy" if is_buy else "sell"}.txt'
        self.drive_logger.write_file(filename, str(product_id))
        return True

    def log_writer_gtt(self, product_id, stock_code, is_buy):
        filename = f'{stock_code}_{"buy_gtt" if is_buy else "sell_gtt"}.txt'
        self.drive_logger.write_file(filename, str(product_id))

    def log_cancel_order(self, stock_code, variety: str, is_buy):
        filename = f'{stock_code}_{"buy" if is_buy else "sell"}.txt'
        if not self.drive_logger.file_exists(filename):
            return False
        product_id = self.drive_logger.read_file(filename)
        try:
            self.broker.cancel_order(
                order_id=int(product_id),
                variety=variety,
                is_buy=is_buy
            )
        except Exception as e:
            #print(e)
            pass
        self.drive_logger.delete_file(filename)
        return True

    @property
    def get_current_time(self):
        return datetime.now().strftime(self.DATETIME_FORMAT)

    def _should_run(self, signal) -> bool:
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        current_day = now.weekday()
        current_time = now.time()
        run_days = set(int(day.strip()) for day in signal['run_on_days'].split(','))
        before_time = datetime.strptime(signal['run_before_time'], self.TIME_FORMAT).time()
        after_time = datetime.strptime(signal['run_after_time'], self.TIME_FORMAT).time()
        if signal.get('is_time_between',False) == True:
            return current_day in run_days and (current_time <= before_time and current_time >= after_time)
        return current_day in run_days and (current_time <= before_time or current_time >= after_time)
