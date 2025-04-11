from pytoniq_core import Address
from tonutils.jetton.dex.stonfi import StonfiRouterV2
from tonutils.jetton.dex.stonfi.v2.pton.constants import PTONAddresses
from tonutils.client import TonapiClient
from tonutils.wallet import (WalletV4R2)
from tonutils.utils import to_amount, to_nano

async def create_wallet():
    client = TonapiClient(api_key=API_KEY)
    wallet, public_key, private_key, mnemonic = WalletV4R2.create(client)
    return wallet.address.to_str(), mnemonic