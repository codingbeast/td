from jugaad_trader import Zerodha

HOMMAGENIUS_CONFIG = {
    "ticker": "NIFTYBEES",
    "stock": "NIFTYBEES",
    "exchange": Zerodha.EXCHANGE_NSE,
    "variety": Zerodha.VARIETY_REGULAR,
    "order_type": Zerodha.ORDER_TYPE_LIMIT,
    "product_type": Zerodha.PRODUCT_CNC,
    "min_sell_qnt": 30,
    "amount": 500,
    "profit_percentage": 1.03,
    "run_before_time": "09:00:00",
    "run_after_time": "15:00:00",
    "run_on_days": "3",
    "is_buy": True,
    "cancel_old_order": False,
    "amount_strict": False,
    "enabled": True
}