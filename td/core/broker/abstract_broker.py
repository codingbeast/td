
"""this is abstract broker class"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AbstractBroker(ABC):
    """_summary_
    Args:
        ABC (_type_): _description_
    """
    @abstractmethod
    def place_order(self, **kwargs) -> Optional[str]:
        """Place an order.
        Accept a single mapping `order` to avoid large positional argument
        lists. Implementations should document expected keys (e.g.,
        `tradingsymbol`, `exchange`, `transaction_type`, etc.).
        """
    @abstractmethod
    def cancel_order(self, order_id: str, variety: str) -> Optional[bool]:
        """Cancel an order."""
    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
