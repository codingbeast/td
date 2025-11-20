"""lahari model configuration."""
from pydantic import field_validator
from .base import StrategyConfig
from .common_enums import (
    Exchange, Variety, OrderType, ProductType
    )

class LahariConfig(StrategyConfig):
    """lahari strategy configuration"""
    ticker: str
    stock: str
    exchange: Exchange
    variety: Variety
    order_type: OrderType
    product_type: ProductType

    min_sell_qnt : int = 10
    uptrand_amount : int = 300
    downtrand_amount : int = 500
    profit_percentage: float

    run_before_time: str
    run_after_time: str
    is_time_between: bool = False
    run_on_days: str = "0,1,2,3,4"

    is_buy: bool = True
    cancel_old_order: bool = False
    amount_strict: bool = False
    enabled: bool = True

    @field_validator("cancel_old_order")
    @classmethod
    def force_cancel_old_order_false(cls, _):
        """Lahari strategy should never cancel old orders."""
        return False #lahari strategy should never cancel old orders
