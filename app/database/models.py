from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List
from config import ENGINE, ECHO

engine = create_async_engine(url=ENGINE, echo=ECHO)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=True)
    address = mapped_column(String)  # Добавляем поле для адреса
    mnemonic = mapped_column(String)  # Добавляем поле для мнемоника
    
class Wallet(Base):
    __tablename__ = 'Wallets'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(512))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)