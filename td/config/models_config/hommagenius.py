"""hommagenius model configuration."""
from .base import StrategyConfig
from .common_enums import (
    Exchange, Variety, OrderType, ProductType
    )

class HommageniusConfig(StrategyConfig):
    """hommagenius strategy configuration"""
    ticker: str
    stock: str
    exchange: Exchange
    variety: Variety
    order_type: OrderType
    product_type: ProductType

    min_sell_qnt: int = 10
    amount: int
    profit_percentage: float

    run_before_time: str
    run_after_time: str
    is_time_between: bool = False
    run_on_days: str = "0,1,2,3,4"

    is_buy: bool = True
    cancel_old_order: bool = True
    amount_strict: bool = False
    enabled: bool = True
