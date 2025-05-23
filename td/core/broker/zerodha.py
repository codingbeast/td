from typing import Optional, Dict, Any
from jugaad_trader import Zerodha
from td.core.broker.abstract_broker import AbstractBroker
from algoconnectorhelper.zerodha.connect_zerodha import getKite


class ZerodhaBroker(AbstractBroker):
    """
    ZerodhaBroker is an implementation of AbstractBroker using Zerodha Kite API.
    """

    def __init__(self, user_id: str, password: str, tpin_token: str):
        """
        Initialize Zerodha client session using user credentials.
        """
        self.kite = getKite(
            user_id=user_id,
            password=password,
            otp_secret_key=tpin_token
        )

    def place_order(
        self,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        variety: str,
        order_type: str,
        price: float,
        product: str,
        disclosed_quantity: int,
        validity: str
    ) -> Any:
        """
        Place an order through Zerodha Kite.
        """
        return self.kite.place_order(
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            variety=variety,
            order_type=order_type,
            price=price,
            product=product,
            disclosed_quantity=disclosed_quantity,
            validity=validity
        )

    def cancel_order(
        self,
        order_id: str,
        variety: str,
        is_buy: bool = True
    ) -> bool:
        """
        Cancel an order in Zerodha.

        :param order_id: ID of the order to cancel
        :param variety: Order variety (e.g., regular, amo)
        :param is_buy: Optional flag to confirm buy-side (default True)
        :return: True if cancelled, False on exception
        """
        try:
            if is_buy:
                self.kite.cancel_order(order_id=order_id, variety=variety)
                return True
            else:
                self.kite.cancel_order(order_id=order_id, variety=variety)
                return True
        except Exception as e:
            pass
            #print(f"Failed to cancel order {order_id}: {e}")
        return False

    def get_positions(self) -> Dict[str, Any]:
        """
        Get current day and net positions.
        """
        positions = self.kite.positions()
        return {
            "net": positions["net"],
            "day": positions["day"]
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
