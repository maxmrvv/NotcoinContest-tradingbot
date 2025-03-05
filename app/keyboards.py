from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Main page', callback_data='to_main')]
])

inline_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🟢 BUY ', callback_data='buy_'), 
    InlineKeyboardButton(text='🔴 SELL', callback_data='sell_')],
    [InlineKeyboardButton(text='Wallet 💸', callback_data='wallet_'),
    InlineKeyboardButton(text='Airdrops 🚀', callback_data='airdrops_')],
    [InlineKeyboardButton(text='Help 📝', callback_data='help_')]
])

wallet_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💸 Deposit', callback_data='deposit_'), 
    InlineKeyboardButton(text='💸 Withdrawal', callback_data='withdrawal_')],
    [InlineKeyboardButton(text='🔐 Show mnemonic', callback_data='showmnemonic_')],
    [InlineKeyboardButton(text='⬅️ Main page', callback_data='to_main')]
])

airdrops_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚀 List of airdrops', callback_data='listairdrop_'), 
    InlineKeyboardButton(text='📝 Create your own airdrop', callback_data='createair_')],
    [InlineKeyboardButton(text='❓ Information', callback_data='infoairdrop_')],
    [InlineKeyboardButton(text='⬅️ Main page', callback_data='to_main')]
])

deposit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Update', callback_data='update_'), 
    InlineKeyboardButton(text='⬅️ Main page', callback_data='to_main')]
])