from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import app.keyboards as kb
import asyncio
import aiohttp

from pytoniq_core import Address
from tonutils.jetton.dex.stonfi import StonfiRouterV2
from tonutils.jetton.dex.stonfi.v2.pton.constants import PTONAddresses
from tonutils.client import TonapiClient
from tonutils.wallet import (WalletV4R2)
from tonutils.utils import to_amount, to_nano

from app.database.request import (set_user, get_user)
import app.keyboards as kb

from config import API_KEY


IS_TESTNET = False

router = Router()

async def create_wallet():
    client = TonapiClient(api_key=API_KEY)
    wallet, public_key, private_key, mnemonic = WalletV4R2.create(client)
    return wallet.address.to_str(), mnemonic

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


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message | CallbackQuery):
    user_id = message.from_user.id
    user = await get_user(user_id)  

    is_callback = isinstance(message, CallbackQuery)

    if is_callback:
        callback_query = message
        await callback_query.answer()  
    else:
        callback_query = None  

    if user:
        mnemonic = user.mnemonic  
        try:
            balance = await get_balance(mnemonic)
            if balance is None or balance < 0:
                balance = 0  

        except Exception as e:

            balance = 0  

        response_text = (
            f"👋 Welcome back to the Notcoin Trading Bot! \n\n"
            f"This bot is designed for convenient crypto trading on the TON blockchain 💎 \n\n"
            f"Your TON wallet: {balance} TON \n\n"
            f"Wallet Address: <code>{user.address}</code> \n\n"
        )
    else:
        address, mnemonic = await create_wallet()
        
        await set_user(user_id, address, mnemonic)
        
        response_text = (
            f"👋 Welcome to the Notcoin Trading Bot! \n\n"
            f"This bot is designed for convenient crypto trading on the TON blockchain 💎 \n\n"
            f"Your TON wallet: 0 TON ($0) \n\n"
            f"Wallet Address: <code>{address}</code>\n\n"
        )

    if callback_query:
        await callback_query.message.edit_text(response_text,reply_markup=kb.inline_main, parse_mode='HTML')
    else:
        await message.answer(response_text,reply_markup=kb.inline_main, parse_mode='HTML')


#Callback`s
@router.callback_query(F.data == 'wallet_')
async def wallet(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    await callback.answer('')
    mnemonic = user.mnemonic

    try:
        balance = await get_balance(mnemonic)
        if balance is None:
            balance = 0  

        await callback.message.edit_text(
            text=f'Your wallet address:\n\n<code>{user.address}</code>\n\nYour balance: {balance}',
            reply_markup=kb.wallet_main, parse_mode='HTML'
        )
    except Exception as e:
        print(f"Error getting balance for user {user_id}: {e}")
        await callback.message.edit_text(
            text=f'Your wallet address:\n\n<code>{user.address}</code>\n\nYour balance: 0 TON',
            reply_markup=kb.wallet_main, parse_mode='HTML'
        )

@router.callback_query(F.data == 'airdrops_')
async def airdrops(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(text='⚡️ There will be an airdrop system from the creators of token for traders of their coins. ⚡️',
                                     reply_markup=kb.airdrops_main)

@router.callback_query(F.data == 'help_')
async def help(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(text='⚡️ Dev: @doxinglove',
                                     reply_markup=kb.to_main)

@router.callback_query(F.data == 'showmnemonic_')
async def wallet(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    await callback.answer('')
    message = await callback.message.edit_text(
        text=f'Your mnemonic:\n\n<code>{user.mnemonic}</code> \n\n This message will be deleted in 30 seconds.',
        reply_markup=kb.to_main, parse_mode='HTML'
    )
    await asyncio.sleep(30)
    await message.delete()

@router.callback_query(F.data == 'deposit_')
async def deposit(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    await callback.answer('')
    mnemonic = user.mnemonic
    
    try:
        balance = await get_balance(mnemonic)
    except Exception as e:
        balance = 0  

    await callback.message.edit_text(
        text=f'Send a ton to your wallet address:\n\n<code>{user.address}</code>\n\nYour TON balance: <code>{balance}</code>',
        reply_markup=kb.deposit, parse_mode='HTML'
    )

@router.callback_query(F.data == 'update_')
async def update(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    await callback.answer('')
    
    mnemonic = user.mnemonic
    balance = await get_balance(mnemonic)
    
    await callback.message.edit_text(
        text=f'Send a ton to your wallet address:\n\n<code>{user.address}</code>\n\nYour TON balance: <code>{balance}</code>',
        reply_markup=kb.deposit, parse_mode='HTML'
    )

class Withdrawal(StatesGroup):
    address = State()
    ton = State()

@router.callback_query(F.data == 'withdrawal_')
async def withdrawal(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)  

    await state.set_state(Withdrawal.address)
    await callback.answer('')  
    await callback.message.answer('⚡️ Enter the address for TON withdrawal:')

@router.message(Withdrawal.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Withdrawal.ton)
    await message.answer('Send the amount of TON you want to withdraw:')

@router.message(Withdrawal.ton)
async def process_amount(message: Message, state: FSMContext):
    amount = message.text.strip()

    try:
        amount_float = float(amount)
    except ValueError:
        await message.answer("Invalid amount. Please enter a valid number.")
        return

    data = await state.get_data()
    destination_address = data.get('address')

    user_id = message.from_user.id
    user = await get_user(user_id)  
    mnemonic = user.mnemonic 


    await send_ton(destination_address, amount_float, mnemonic)
    await message.answer(f"Successfully sent {amount_float} TON to {destination_address}.")
    
    await state.clear()


async def send_ton(destination_address: str, transfer_amount: float, mnemonic: str):
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, public_key, private_key, _ = WalletV4R2.from_mnemonic(client, mnemonic)

    comment = "Notcoin Trading Bot by maxmrvv"
    body = await wallet.build_encrypted_comment_body(
        text=comment,
        destination=destination_address,
    )

    tx_hash = await wallet.transfer(
        destination=destination_address,
        amount=transfer_amount,
        body=body,
    )


class Swap(StatesGroup):
    token_address = State()
    amount = State()

TO_JETTON_MASTER_ADDRESS = "EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"  # Адрес Jetton Master


@router.callback_query(F.data == 'buy_')
async def buy(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')

    
    await callback.message.answer("Please send the token address you want to purchase:")
    
    
    await state.set_state(Swap.token_address)

@router.message(Swap.token_address)
async def handle_token_address(message: Message, state: FSMContext):
    token_address = message.text.strip()
    
    
    await state.update_data(token_address=token_address)
    
    await message.answer("Please send the amount of TON you want to swap:")
    
    
    await state.set_state(Swap.amount)

@router.message(Swap.amount)
async def handle_amount(message: Message, state: FSMContext):
    amount = message.text.strip()

    try:
        amount_float = float(amount)  
        if amount_float <= 0:
            raise ValueError("Amount must be a positive number.")
    except ValueError:
        await message.answer("Invalid amount. Please enter a valid positive number.")
        return

    user_id = message.from_user.id
    user = await get_user(user_id)  
    mnemonic = user.mnemonic  

    token_address = (await state.get_data()).get('token_address')

    try:
        
        await perform_swap(token_address, amount_float, mnemonic)
        await message.answer("Successfully swapped TON to Jetton!")
    except Exception as e:
        await message.answer(f"Error during swap: {str(e)}")
    
    await state.clear()



async def perform_swap(token_address: str, ton_amount: float, mnemonic: str):
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, _, _, _ = WalletV4R2.from_mnemonic(client, mnemonic)

    
    router_address = await get_router_address(ton_amount)  
    stonfi_router = StonfiRouterV2(client, router_address=Address(router_address))

    to, value, body = await stonfi_router.get_swap_ton_to_jetton_tx_params(
        user_wallet_address=wallet.address,
        receiver_address=wallet.address,
        offer_jetton_address=Address(token_address),
        offer_amount=to_nano(ton_amount),
        min_ask_amount=0,
        refund_address=wallet.address,
    )

    tx_hash = await wallet.transfer(
        destination=to,
        amount=to_amount(value),
        body=body,
    )

    print(f"Successfully swapped TON to Jetton! Transaction hash: {tx_hash}")

async def get_router_address(ton_amount: float) -> str:
    url = "https://api.ston.fi/v1/swap/simulate"
    headers = {"Accept": "application/json"}

    params = {
        "offer_address": PTONAddresses.TESTNET if IS_TESTNET else PTONAddresses.MAINNET,
        "ask_address": TO_JETTON_MASTER_ADDRESS,
        "units": to_nano(ton_amount),  
        "slippage_tolerance": 1,
        "dex_v2": "true",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params, headers=headers) as response:
            if response.status == 200:
                content = await response.json()
                return content.get("router_address")
            else:
                error_text = await response.text()
                raise Exception(f"Failed to get router address: {response.status}: {error_text}")



JETTON_DECIMALS = 1

class SellJettonStates(StatesGroup):
    waiting_for_token_address = State()
    waiting_for_jetton_amount = State()

@router.callback_query(F.data == 'sell_')
async def sell_jetton(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text(text='Enter the address of the token for sale:')
    await state.set_state(SellJettonStates.waiting_for_token_address.state) 

@router.message(SellJettonStates.waiting_for_token_address)
async def process_token_address(message: types.Message, state: FSMContext):
    token_address = message.text.strip()
    await state.update_data(token_address=token_address)

    await message.answer("Enter the amount of Jetton for sale:")
    await state.set_state(SellJettonStates.waiting_for_jetton_amount.state) 

@router.message(SellJettonStates.waiting_for_jetton_amount)
async def process_jetton_amount(message: types.Message, state: FSMContext):
    amount = message.text.strip()

    try:
        amount_float = float(amount)  
        if amount_float <= 0:
            raise ValueError("The quantity must be a positive number.")
    except ValueError:
        await message.answer("Incorrect quantity. Please enter the correct positive number.")
        return

    user_id = message.from_user.id
    user = await get_user(user_id)  
    mnemonic = user.mnemonic  

    token_address = (await state.get_data()).get('token_address')

    try:
        await perform_sell(token_address, amount_float, mnemonic)
        await message.answer("Successfully sold by Jetton!")
    except Exception as e:
        await message.answer(f"Error when selling: {str(e)}")
    
    await state.clear()  

async def perform_sell(token_address: str, jetton_amount: float, mnemonic: str):
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, _, _, _ = WalletV4R2.from_mnemonic(client, mnemonic)

    router_address = await get_router_address(token_address, jetton_amount)  
    stonfi_router = StonfiRouterV2(client, router_address=Address(router_address))

    to, value, body = await stonfi_router.get_swap_jetton_to_ton_tx_params(
        offer_jetton_address=Address(token_address),
        receiver_address=wallet.address,
        user_wallet_address=wallet.address,
        offer_amount=to_nano(jetton_amount, JETTON_DECIMALS),
        min_ask_amount=0,
        refund_address=wallet.address,
    )

    tx_hash = await wallet.transfer(
        destination=to,
        amount=to_amount(value),
        body=body,
    )

    print("Successfully swapped Jetton to TON!")
    print(f"Transaction hash: {tx_hash}")

async def get_router_address(token_address: str, jetton_amount: float) -> str:
     url = "https://api.ston.fi/v1/swap/simulate"
     headers = {"Accept": "application/json"}

     params = {
        "offer_address": token_address,
        "ask_address": PTONAddresses.TESTNET if IS_TESTNET else PTONAddresses.MAINNET,
        "units": to_nano(jetton_amount, JETTON_DECIMALS), 
        "slippage_tolerance": 1,
        "dex_v2": "true",
    }

     async with aiohttp.ClientSession() as session:
         async with session.post(url, params=params, headers=headers) as response:
            if response.status == 200:
                content = await response.json()
                return content.get("router_address")
            else:
                error_text = await response.text()
                raise Exception(f"Couldn't get router address: {response.status}: {error_text}")
