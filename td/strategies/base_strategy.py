from abc import ABC, abstractmethod
from td.core.data.historical import HistoricalData

class BaseStrategy(ABC):
    def __init__(self, config):
        self.config = config
        self.data_client = HistoricalData()
    
    @abstractmethod
    def generate_signals(self):
        """Generate trading signals based on strategy logic"""
        pass
    
    @abstractmethod
    def calculate_position_size(self):
        """Calculate appropriate position size"""
        pass
    
    @property
    def name(self):
        return self.__class__.__name__