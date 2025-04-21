from jugaad_trader import Zerodha
from datetime import datetime
class OrderManager:
    def __init__(self, broker, drive_logger, message_logger):
        self.broker = broker
        self.drive_logger = drive_logger
        self.message_logger = message_logger
    
    def execute_strategy_orders(self, strategy):
        """Execute buy/sell orders based on strategy signals"""
        strategy.set_broker(self.broker)
        signals = strategy.generate_signals()
        for signal in signals:
            if signal['action'] == 'BUY':
                self._execute_buy(signal)
            elif signal['action'] == 'SELL':
                self._execute_sell(signal)
            elif signal['action'] == 'BUY_SELL':
                self._execute_buy_sell(signal)
    
    def _execute_buy(self, signal):
        """Execute a BUY order with the broker"""
        try:
            self.message_logger.info(f"Attempting BUY order for {signal['symbol']}")
            self.log_cancel_order(signal['symbol'], self.broker, True)
            # Prepare order parameters
            order_params = {
                'tradingsymbol': signal['symbol'],
                'exchange': self.broker.EXCHANGE_NSE,
                'transaction_type': self.broker.TRANSACTION_TYPE_BUY,
                'quantity': signal['quantity'],
                'variety': self.broker.VARIETY_AMO,
                'order_type': self.broker.ORDER_TYPE_LIMIT,
                'price': round(float(signal['price']), 2),
                'product': self.broker.PRODUCT_CNC,
                'validity': self.broker.VALIDITY_DAY,
                'disclosed_quantity': min(signal['quantity'], 
                                    max(1, round(signal['quantity'] * 0.1)))  # 10% or at least 1
            }
            
            # Place the order
            order_id = self.broker.place_order(**order_params)
            self.log_writer_order(order_id, signal['symbol'], True)
            # Log successful order
            self.message_logger.info(f"BUY order placed - ID: {order_id} | "
                            f"{signal['quantity']} shares of {signal['symbol']} "
                            f"@ {signal['price']}")
            
            return {
                'status': 'SUCCESS',
                'order_id': order_id,
                'details': order_params
            }
            
        except Exception as e:
            error_msg = f"Failed BUY order for {signal['symbol']}: {str(e)}"
            self.message_logger.error(error_msg)
            return {
                'status': 'FAILED',
                'error': error_msg,
                'details': signal
            }
    def _execute_sell(self, signal):
        # Implement sell logic with proper error handling
        print("called sell order")
        pass
    def _execute_buy_sell(self, signal):
        # Implement sell logic with proper error handling
        print("called buy sell order")
        pass

    def log_writer_order(self, productID, stock_code, isbuy):
        filename = f'{stock_code}_{"buy" if isbuy else "sell"}.txt'
        self.drive_logger.write_file(filename, str(productID))
        return True

    def log_writer_gtt(self, productID, stock_code, isbuy):
        filename = f'{stock_code}_{"buy_gtt" if isbuy else "sell_gtt"}.txt'
        self.drive_logger.write_file(filename, str(productID))

    def log_cancel_order(self, stock_code, kite: Zerodha, isbuy):
        filename = f'{stock_code}_{"buy" if isbuy else "sell"}.txt'
        if not self.drive_logger.file_exists(filename):
            return False
            
        productID = self.drive_logger.read_file(filename)
        gtt_order_id = int(productID)

        try:
            kite.cancel_order(order_id=gtt_order_id, variety=kite.VARIETY_AMO)
        except Exception:
            pass

        self.drive_logger.delete_file(filename)
        return True

    @property
    def getCurrentTime(self):
        current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        return current_datetime