# pylint: disable=missing-docstring
from importlib import import_module
from typing import Type
from td.strategies.base_strategy import BaseStrategy

def get_strategy(strategy_name: str, config: dict) -> 'BaseStrategy':
    """
    Factory function to instantiate strategy classes
    Args:
        strategy_name: Name of the strategy (e.g., 'goldbees')
        config: Configuration dictionary for the strategy
    Returns:
        Initialized strategy instance
    """
    try:
        module = import_module(f'td.strategies.{strategy_name.lower()}')
        strategy_class = getattr(module, f'{strategy_name.capitalize()}Strategy')
        return strategy_class(config)  # Initialize with config
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not initialize strategy: {e}") from e
