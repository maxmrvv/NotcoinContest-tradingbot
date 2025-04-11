from pytoniq_core import Address
from tonutils.jetton.dex.stonfi import StonfiRouterV2
from tonutils.jetton.dex.stonfi.v2.pton.constants import PTONAddresses
from tonutils.client import TonapiClient
from tonutils.wallet import (WalletV4R2)
from tonutils.utils import to_amount, to_nano

async def get_balance(mnemonic):
    client = TonapiClient(api_key=API_KEY)
    wallet, public_key, private_key, mnemonic = WalletV4R2.from_mnemonic(client, mnemonic)
    
    balance = await wallet.balance()
def to_amount(balance):
    return balance / 1_000_000_000  

async def get_balance(mnemonic):
    try:
        client = TonapiClient(api_key=API_KEY)
        wallet, public_key, private_key, mnemonic = WalletV4R2.from_mnemonic(client, mnemonic)
        balance = await wallet.balance()
        return to_amount(balance)  
    except ValueError as e:
        print(f"Ошибка получения баланса: {e}")
        return "Ошибка получения баланса."