"""/td/config/models_config/common_enums.py"""
from enum import Enum

class Exchange(str, Enum):
    """select exchange"""
    NSE = "NSE"
    BSE = "BSE"

class Variety(str, Enum):
    """select variety"""
    AMO = "amo"
    REGULAR = "regular"

class OrderType(str, Enum):
    """select order type"""
    LIMIT = "LIMIT"
    MARKET = "MARKET"

class ProductType(str, Enum):
    """select product type"""
    CNC = "CNC"
    MIS = "MIS"