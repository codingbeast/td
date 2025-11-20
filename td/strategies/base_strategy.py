"""this is base strategy file"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional

import pytz
from td.core.data.historical import HistoricalData


class BaseStrategy(ABC):
    """Base strategy template"""
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"
    def __init__(self, config):
        self.config = config                     # Pydantic model
        self.broker = None
        self.data_client: Optional[HistoricalData] = None
        self.current_action = None
        

    def _create_signal(self, action: str, quantity: int, price: float, **extra) -> Dict[str, Any]:
        """
        Create signal dynamically from config model.
        No need to update when new fields are added.
        """

        # START with mandatory fields
        base_signal = {
            "action": action.upper(),
            "symbol": getattr(self.config, "ticker", None) 
                      or getattr(self.config, "stock", None),
            "quantity": quantity,
            "price": round(float(price), 2),
            "timestamp": datetime.now().isoformat()
        }

        # Dump CONFIG with safe conversion (Enforce enums → strings)
        config_dict = self.config.model_dump(mode="json", by_alias=True)

        # Merge config values into signal
        base_signal.update(config_dict)

        # Override with strategy-specific values
        # Convert Enum → string inside extra
        clean_extra = {
            k: (v.value if hasattr(v, "value") else v)
            for k, v in extra.items()
        }

        base_signal.update(clean_extra)


        return base_signal

    def _create_buy_signal(self, quantity: int, price: float, **extra):
        return self._create_signal("BUY", quantity, price, **extra)

    def _create_sell_signal(self, quantity: int, price: float, **extra):
        return self._create_signal("SELL", quantity, price, **extra)
    
    def create_buy_signal(self, **kwargs):
        """this will use to genrate buy signal"""
        return self._create_buy_signal(**kwargs)
    
    def create_sell_signal(self, **kwargs):
        """this will use to genrate sell signal"""
        return self._create_sell_signal(**kwargs)

    # -----------------------------
    # Required Strategy Methods
    # -----------------------------
    @abstractmethod
    def generate_signals(self) -> List[Dict]:
        """Generate trading signals"""

    @abstractmethod
    def calculate_position_size(self) -> int:
        """Calculate position size"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return strategy name"""

    # -----------------------------
    # Helpers
    # -----------------------------
    def set_broker(self, broker) -> None:
        """set the broker"""
        self.broker = broker
        self.data_client = HistoricalData(self.broker)
    @property
    def get_data_client(self) -> HistoricalData:
        """_summary_

        Raises:
            RuntimeError: _description_

        Returns:
            HistoricalData: _description_
        """
        if self.data_client is None:
            raise RuntimeError("Data client not initialized — call set_broker() first.")
        return self.data_client

    def _should_run_now(self) -> bool:
        import pytz
        from datetime import datetime

        cfg = self.config
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)

        # Day Filter
        allowed_days = {int(d) for d in cfg.run_on_days.split(",")}
        if now.weekday() not in allowed_days:
            return False

        before = datetime.strptime(cfg.run_before_time, "%H:%M:%S").time()
        after = datetime.strptime(cfg.run_after_time, "%H:%M:%S").time()
        current = now.time()

        # AUTO-FIX: detect swapped times
        # Example wrong input: before=09:00, after=15:00
        # Correct interpretation: after=09:00, before=15:00
        if after > before:
            # swap times because window is reversed
            after, before = before, after
        # ---- RUN ONLY BETWEEN ----
        if cfg.is_time_between:
            return after <= current <= before

        # ---- RUN OUTSIDE WINDOW ----
        return current <= after or current >= before

