from app.database.models import User
from app.database.models import async_session

from sqlalchemy import select, update, delete

async def set_user(tg_id, address, mnemonic):
    async with async_session() as session:

        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:

            mnemonic_str = ' '.join(mnemonic)  
            new_user = User(tg_id=tg_id, address=address, mnemonic=mnemonic_str)

            session.add(new_user)
            await session.commit()

async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))
