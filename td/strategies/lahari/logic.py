"""/td/strategies/hommagenius/logic.py"""
from pandas import DataFrame
from td.core.logging.console_logger import log
from td.core.logging.google_drive import FlagManager
from td.strategies.lahari.utils import calculate_total_shares,get_holding, is_stock_in_position
from .signals import build_buy_signal, build_sell_signal,build_check_signal


LIMIT_PRICES_UP = [200, 500, 400, 300, 400, 500, 600, 700 ]
LIMIT_PRICES_DOWN = [50, 300, 400, 500, 600, 700, 800, 900 ]

def _get_price_data(limit_prices : list[int], new_total : int):
    """get price data"""
    current_total = sum(limit_prices)
    scaling_factor = new_total / current_total
    adjusted_prices = [price * scaling_factor for price in limit_prices]
    adjusted_prices = [round(i) for i in adjusted_prices]
    return adjusted_prices

def _gen_up(strategy, price : int, flag : bool):
    """generate up stock data"""
    limit_prices = _get_price_data(limit_prices = LIMIT_PRICES_UP, 
                                   new_total= strategy.config.uptrand_amount
                                   )
    final_prices = [price-0.3,  price - 0.6,
                    price - 0.9, price - 1.2,
                    price - 1.5, price - 1.8,
                    price - 2.1, price - 2.4 ]
    temp = []
    for i,j in zip(limit_prices, final_prices):
        qnt = calculate_total_shares(strategy,i,j)
        temp.append({
            "price" : round(j, 2),
            "qnt" : qnt,
            "is_up_trand" : flag
        })
    return temp

def _gen_down(strategy, price : int, flag : bool):
    """generate down stock data"""
    limit_prices = _get_price_data(limit_prices = LIMIT_PRICES_DOWN,
                                   new_total= strategy.config.downtrand_amount
                                   )
    final_prices = [price - 0.3, price - 0.7,
                    price - 1.4, price - 2.1,
                    price - 2.8, price - 3.5,
                    price - 4.2, price - 4.9]
    temp = []
    for i,j in zip(limit_prices, final_prices):
        qnt = calculate_total_shares(strategy,i,j)
        temp.append({
            "price" : round(j, 2),
            "qnt" : qnt,
            "is_up_trand" : flag
        })
    return temp

def _gen_stock_data(strategy, stock_data : DataFrame):
    """generate stock data"""
    historydata = [round(i,2) for i in list(stock_data['CLOSE'])]
    avg_price = historydata[-1]
    avg_price2 = sum(historydata[-2:])/2
    avg_price3 = sum(historydata[-3:])/3
    avg_price4 = sum(historydata[-4:])/4
    avg_price5 = sum(historydata[-5:])/5
    final_avg_price = round(sum([avg_price2, avg_price3, avg_price4, avg_price5])/4,2)
    is_up_trand = avg_price > final_avg_price
    log.info("market isUPTRAND : %s",is_up_trand)
    log.info("current Price : %s",avg_price)
    log.info("uptrand Price : %s",final_avg_price)
    if is_up_trand:
        final_stock_data = _gen_up(strategy, price = avg_price, flag = is_up_trand)
    else:
        final_stock_data = _gen_down(strategy, price = avg_price, flag = is_up_trand)
    return final_stock_data

def buy_logic(strategy,get_stock_data):
    """buy logic"""
    stock_data_init = get_stock_data(strategy)
    gen_stock_data = _gen_stock_data(strategy, stock_data_init)
    manager = FlagManager()
    is_flag_set = False
    buy_build_container = []
    for stock in gen_stock_data:
        if is_flag_set is False:
            manager.update_flag(stock['is_up_trand'])
            is_flag_set = True
        if not manager.check_flags():
            continue
        buy_build_container.append(
            build_buy_signal(strategy,qty=stock['qnt'], price=stock['price'])
        )
    return buy_build_container

def sell_logic(strategy):
    """sell logic"""
    holding = get_holding(strategy)
    if not holding:
        return []
    sell_price = max(
        holding['average_price'] * strategy.config.profit_percentage,
        holding['last_price']
    )
    sell_qnt = holding['quantity']
    sell_qnt = sell_qnt if strategy.config.min_sell_qnt < sell_qnt else 0
    return [
        build_sell_signal(strategy,qty=sell_qnt, price=sell_price)
    ]

def check_logic(strategy,get_stock_data):
    """check logic"""
    is_in_position = is_stock_in_position(strategy)
    if is_in_position:
        return []
    stock_data_init = get_stock_data(strategy)
    gen_stock_data = _gen_stock_data(strategy, stock_data_init)
    buy_build_container = []
    for stock in gen_stock_data:
        buy_build_container.append(
            build_check_signal(strategy,qty=stock['qnt'], price=stock['price'])
        )
        break #only single order should place on check point
    return buy_build_container
