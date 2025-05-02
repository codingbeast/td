from jugaad_trader import Zerodha

GOLDBEES_CONFIG = {
    "ticker": "GOLDBEES",
    "stock": "GOLDBEES",
    "exchange": Zerodha.EXCHANGE_NSE,
    "variety": Zerodha.VARIETY_AMO,
    "order_type": Zerodha.ORDER_TYPE_LIMIT,
    "product_type": Zerodha.PRODUCT_CNC,
    "min_sell_qnt": 2,
    "amount": 100,
    "reduce": 0.30,
    "profit_percentage": 1.02,
    "run_before_time": "09:00:00",
    "run_after_time": "15:00:00",
    "run_on_days": "0,1,2,3,4",
    "is_buy": True,
    "amount_strict": False,
    "enabled": True
}