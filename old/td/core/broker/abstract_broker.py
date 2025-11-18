
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AbstractBroker(ABC):
    @abstractmethod
    def place_order(self, **kwargs) -> str:
        """Place an order"""
        pass
        
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
        
    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        pass