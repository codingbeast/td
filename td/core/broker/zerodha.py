"""this is zerodha broker implementation"""
# pylint: disable=broad-exception-caught
from typing import Dict, Any, cast
import json
from td.core.broker.abstract_broker import AbstractBroker
from td.core.broker.connect_zerodha import get_kite

class ZerodhaBroker(AbstractBroker):
    """
    ZerodhaBroker is an implementation of AbstractBroker using Zerodha Kite API.
    """

    def __init__(self, user_id: str, password: str, tpin_token: str):
        """
        Initialize Zerodha client session using user credentials.
        """
        self.kite = get_kite(
            user_id=user_id,
            password=password,
            otp_secret_key=tpin_token
        )

    def place_order(self, **kwargs) -> Any:
        """
        Place an order through Zerodha Kite using keyword arguments.
        OrderManager sends kwargs, so we must accept kwargs.
        """
        try:
            return self.kite.place_order(**kwargs)
        except TypeError:
            # fallback: manually map fields (rarely needed)
            return self.kite.place_order(
                tradingsymbol=kwargs.get("tradingsymbol"),
                exchange=kwargs.get("exchange"),
                transaction_type=kwargs.get("transaction_type"),
                quantity=kwargs.get("quantity"),
                variety=kwargs.get("variety"),
                order_type=kwargs.get("order_type"),
                price=kwargs.get("price"),
                product=kwargs.get("product"),
                disclosed_quantity=kwargs.get("disclosed_quantity"),
                validity=kwargs.get("validity"),
            )


    def cancel_order(
        self,
        order_id: str,
        variety: str,
    ) -> bool:
        """
        Cancel an order in Zerodha.

        :param order_id: ID of the order to cancel
        :param variety: Order variety (e.g., regular, amo)
        :param is_buy: Optional flag to confirm buy-side (default True)
        :return: True if cancelled, False on exception
        """
        try:
            # cancel_order behavior is the same for buy/sell here; call once
            self.kite.cancel_order(order_id=order_id, variety=variety)
            return True
        except Exception:
            # Intentionally swallow broker errors here to avoid raising from
            # a cancel attempt; callers receive False on failure.
            pass
        return False

    def get_positions(self) -> Dict[str, Any]:
        """
        Get current day and net positions.
        """
        positions = self.kite.positions()

        # Kite client may return bytes, a JSON string, or a mapping-like
        # object. Coerce into a dict and use .get() to avoid type-checker
        # complaints about __getitem__ overloads.
        if isinstance(positions, (bytes, bytearray)):
            try:
                positions = json.loads(positions.decode())
            except Exception:
                positions = {}
        elif isinstance(positions, str):
            try:
                positions = json.loads(positions)
            except Exception:
                positions = {}

        if not isinstance(positions, dict):
            try:
                positions = dict(positions)
            except Exception:
                positions = {}

        positions = cast(Dict[str, Any], positions)
        return {
            "net": positions.get("net"),
            "day": positions.get("day"),
        }

    def get_holdings(self) -> Any:
        """
        Get current holdings.
        """
        return self.kite.holdings()
    def get_margins(self) -> Any:
        """
        Get margin details.
        """
        return self.kite.margins()
    def historical_data(self, instrument_token, from_date_str, to_date_str, period = 'day'):
        """access historical data from zerodha broker"""
        return self.kite.historical_data(instrument_token=instrument_token,
                                         from_date=from_date_str,
                                         to_date=to_date_str,
                                         interval=period)
