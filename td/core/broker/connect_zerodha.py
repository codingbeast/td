"""this module contains function to connect to zerodha broker"""
import os
import pickle
import time
import pyotp
from jugaad_trader import Zerodha

def get_kite(user_id: str, password: str, otp_secret_key: str) -> Zerodha:
    """
    Returns an instance of Zerodha class after authentication.

    Args:
        user_id (str): The Zerodha user ID.
        password (str): The Zerodha account password.
        otp_secret_key (str): The OTP secret key for two-factor authentication.

    Returns:
        Zerodha: An instance of the Zerodha class.
    """
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    # Construct the token path
    token_path = os.path.join(home_dir, ".enctoken_zerodha.pkl") 
    if os.path.exists(token_path):
        with open(token_path, 'rb') as f:
            enctoken = pickle.load(f)
            kite = Zerodha()
            kite.enc_token = enctoken
            try:
                profile = kite.profile()
                return kite
            except:
                pass
    while True:
        authkey = pyotp.TOTP(otp_secret_key)
        kite = Zerodha()
        kite.user_id = user_id
        kite.password = password
        j = kite.login_step1()
        kite.twofa = authkey.now()
        j = kite.login_step2(j)
        with open(token_path, 'wb') as f:
            pickle.dump(kite.r.cookies['enctoken'], f)
        kite.enc_token = kite.r.cookies['enctoken']
        try:
            profile = kite.profile()
            return kite
        except:
            time.sleep(60)
            pass