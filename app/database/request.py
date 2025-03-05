from app.database.models import User
from app.database.models import async_session

from sqlalchemy import select, update, delete

from tonutils.client import TonapiClient
from tonutils.wallet import (WalletV4R2)


async def create_wallet():
    wallet = Wallet()  # type: ignore
    mnemonic = wallet.generate_mnemonic()  # Генерация мнемоника
    address = wallet.get_address()  # Получение адреса
    return address, mnemonic

async def set_user(tg_id, address, mnemonic):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            # Преобразуем список мнемоников в строку
            mnemonic_str = ' '.join(mnemonic)  # Используйте пробел или другой разделитель по вашему выбору
            
            new_user = User(tg_id=tg_id, address=address, mnemonic=mnemonic_str)
            session.add(new_user)
            await session.commit()


async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))
