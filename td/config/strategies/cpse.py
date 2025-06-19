from jugaad_trader import Zerodha

CPSE_CONFIG = {
    "ticker": "CPSEETF",
    "stock": "CPSEETF",
    "exchange": Zerodha.EXCHANGE_NSE,
    "variety": Zerodha.VARIETY_AMO,
    "order_type": Zerodha.ORDER_TYPE_LIMIT,
    "product_type": Zerodha.PRODUCT_CNC,
    "min_sell_qnt": 2,
    "uptrand_price": 8000,
    "downtrand_price": 10000,
    "profit_percentage": 1.03,
    "run_before_time": "09:00:00",
    "run_after_time": "15:00:00",
    "is_time_between" : False,
    "run_on_days": "0,1,2,3,4",
    "is_buy": True,
    "cancel_old_order": False,
    "amount_strict": False,
    "enabled": True
}