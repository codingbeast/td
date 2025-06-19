from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime
from td.core.data.historical import HistoricalData


class BaseStrategy(ABC):
    def __init__(self, config: Dict):
        self.config = config
        self.data_client = HistoricalData()
        self.broker = None
        self.current_action = None

    @abstractmethod
    def generate_signals(self) -> List[Dict]:
        """Generate trading signals"""
        pass

    @abstractmethod
    def calculate_position_size(self) -> int:
        """Calculate position size"""
        pass

    def _create_signal(
        self,
        action: str,
        symbol: str,
        quantity: int,
        price: float,
        run_before_time: str = None,
        run_after_time: str = None,
        is_time_between : bool = False,
        run_on_days: str = None,
        order_type: str = "LIMIT",
        variety: str = "regular",
        exchange: str = "NSE",
        product_type : str = "CNC",
        amount_strict: bool = False,
        enabled: bool = True,
        cancel_old_order : bool = True
    ) -> Dict:
        """
        Create a standardized signal dictionary.
        """
        return {
            "action": action.upper(),
            "symbol": symbol,
            "quantity": quantity,
            "price": round(float(price), 2),
            "order_type": order_type,
            "product_type" : product_type,
            "variety": variety,
            "exchange": exchange,
            "amount_strict": amount_strict,
            "enabled": enabled,
            "run_before_time": run_before_time,
            "run_after_time": run_after_time,
            "is_time_between": is_time_between,
            "run_on_days": run_on_days,
            "timestamp": datetime.now().isoformat(),
            "cancel_old_order" : cancel_old_order
        }

    def _create_buy_signal(
        self,
        symbol: str,
        quantity: int,
        price: float,
        run_before_time: str = None,
        run_after_time: str = None,
        is_time_between: bool = False,
        run_on_days: str = None,
        order_type: str = "LIMIT",
        variety: str = "regular",
        exchange: str = "NSE",
        product_type : str = "CNC",
        amount_strict: bool = False,
        enabled: bool = True,
        cancel_old_order: bool = True
    ) -> Dict:
        """
        Create a standardized BUY signal.
        """
        return self._create_signal(
            action="BUY",
            symbol=symbol,
            quantity=quantity,
            price=price,
            run_before_time=run_before_time,
            run_after_time=run_after_time,
            is_time_between=is_time_between,
            run_on_days=run_on_days,
            order_type=order_type,
            variety=variety,
            exchange=exchange,
            product_type=product_type,
            amount_strict=amount_strict,
            enabled=enabled,
            cancel_old_order=cancel_old_order
        )

    def _create_sell_signal(
        self,
        symbol: str,
        quantity: int,
        price: float,
        run_before_time: str = None,
        run_after_time: str = None,
        is_time_between: bool = False,
        run_on_days: str = None,
        order_type: str = "LIMIT",
        variety: str = "regular",
        exchange: str = "NSE",
        product_type : str = "CNC",
        amount_strict: bool = False,
        enabled: bool = True,
        cancel_old_order: bool = True
    ) -> Dict:
        """
        Create a standardized SELL signal.
        """
        return self._create_signal(
            action="SELL",
            symbol=symbol,
            quantity=quantity,
            price=price,
            run_before_time=run_before_time,
            run_after_time=run_after_time,
            is_time_between=is_time_between,
            run_on_days=run_on_days,
            order_type=order_type,
            variety=variety,
            exchange=exchange,
            product_type=product_type,
            amount_strict=amount_strict,
            enabled=enabled,
            cancel_old_order=cancel_old_order
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the strategy"""
        pass

    def set_broker(self, broker) -> None:
        """Set broker instance"""
        self.broker = broker
