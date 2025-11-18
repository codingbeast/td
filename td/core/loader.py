"""td/core/loader.py"""
# pylint: disable=broad-exception-caught
import pkgutil
import importlib
from inspect import isclass
from logging import getLogger
from pathlib import Path
from td.strategies.base_strategy import BaseStrategy

logger = getLogger(__name__)

def discover_strategies(package_name="td.strategies"):
    """Discover strategy classes including sub-packages."""
    strategies = {}

    try:
        pkg = importlib.import_module(package_name)
    except ModuleNotFoundError:
        return strategies

    # `pkg.__file__` may be None for namespace packages; prefer __file__,
    # otherwise fall back to first entry of __path__ if available.
    pkg_file = getattr(pkg, "__file__", None)
    if pkg_file:
        pkg_path = Path(pkg_file).parent
    else:
        pkg_paths = getattr(pkg, "__path__", None)
        if pkg_paths:
            # pkg.__path__ is an iterable of path strings
            pkg_path = Path(next(iter(pkg_paths)))
        else:
            logger.warning("Could not determine package path for %s", package_name)
            return strategies

    # Walk all modules & sub-packages recursively
    for module_info in pkgutil.walk_packages([str(pkg_path)], prefix=pkg.__name__ + "."):
        module_name = module_info.name

        # Skip private or cache modules
        if ".__" in module_name or module_name.endswith(".__pycache__"):
            continue

        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        # Search for classes
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if isclass(obj) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                key = obj.__name__.replace("Strategy", "")
                strategies[key] = obj

    return strategies
