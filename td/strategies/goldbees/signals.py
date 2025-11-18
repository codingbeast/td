"""/td/strategies/goldbees/signals.py"""

def build_buy_signal(strategy, qty, price):
    """_summary_

    Args:
        strategy (_type_): _description_
        qty (_type_): _description_
        price (_type_): _description_

    Returns:
        _type_: _description_
    """
    return strategy.create_buy_signal(
        quantity=qty,
        price=price,
        run_before_time=strategy.config.run_before_time,
        run_after_time=strategy.config.run_after_time,
        run_on_days=strategy.config.run_on_days,
        order_type=strategy.config.order_type,
        variety=strategy.config.variety,
        exchange=strategy.config.exchange,
        enabled=strategy.config.enabled,
        cancel_old_order=strategy.config.cancel_old_order
    )


def build_sell_signal(strategy, qty, price):
    """_summary_

    Args:
        strategy (_type_): _description_
        qty (_type_): _description_
        price (_type_): _description_

    Returns:
        _type_: _description_
    """
    return strategy.create_sell_signal(
        quantity=qty,
        price=price,
        run_before_time=strategy.config.run_before_time,
        run_after_time=strategy.config.run_after_time,
        run_on_days=strategy.config.run_on_days,
        order_type=strategy.config.order_type,
        variety=strategy.config.variety,
        exchange=strategy.config.exchange,
        enabled=strategy.config.enabled,
        cancel_old_order=strategy.config.cancel_old_order
    )
