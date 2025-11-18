"""/td/core/engine.py"""
from td.core.loader import discover_strategies


class Engine:
    """
    Engine that:
    - Accepts a validated Pydantic config model
    - Discovers strategy classes dynamically
    - Instantiates a strategy using only the config model
    """

    def __init__(self, config_model, data, strategies_pkg="td.strategies"):
        self.config_model = config_model      # Pydantic model
        self.data = data                      # external data (optional)
        self.strategies = discover_strategies(strategies_pkg)

    def create_strategy(self):
        """Instantiate strategy from config model."""
        strategy_name = self.config_model.strategy

        if strategy_name not in self.strategies:
            raise ValueError(
                f"Strategy '{strategy_name}' not found. Available: {list(self.strategies.keys())}"
            )

        strategy_class = self.strategies[strategy_name]

        # Create strategy instance with ONLY config
        strategy = strategy_class(self.config_model)

        # DO NOT set data_client here — strategy.set_broker() will do that

        # Optional: attach raw data if you want
        strategy.raw_data = self.data

        return strategy

    def run(self):
        """Create strategy and run it."""
        strategy = self.create_strategy()
        return strategy.generate_signals()
