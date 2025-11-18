"""this is a base model for strategy configuration"""
from pydantic import BaseModel, Field
from .common_enums import (
    Exchange, Variety, OrderType, ProductType
    )

class StrategyConfig(BaseModel):
    """base model for strategy configuration"""
    strategy: str
    ticker: str = Field(..., description="Symbol / Ticker name")
    stock: str = Field(..., description="Underlying stock name")
    exchange: Exchange
    variety: Variety
    order_type: OrderType
    product_type: ProductType
    enabled: bool = Field(True, description="Enable or disable the strategy")
    amount: int = Field(..., description="Amount of the order")
    profit_percentage: float = Field(..., description="Profit percentage for the strategy")
    run_before_time: str = Field(..., description="Time before which the strategy should run")
    run_after_time: str = Field(..., description="Time after which the strategy should run")
    run_on_days: str = Field("0,1,2,3,4", description="Days on which the strategy should run")
    is_time_between: bool = Field(False, description="Whether the strategy should run between \
        the specified times")
    is_buy: bool = Field(True, description="Whether the strategy should buy or sell")
    validity: str = Field("DAY", description="Order validity")
    cancel_old_order: bool = Field(True, description="Whether to cancel old orders")
    amount_strict: bool = Field(False, description="Whether to strictly use the specified amount")
