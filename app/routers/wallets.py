from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db_depends import get_async_db

from app.schemas import WalletBalance as WalletBalanceSchema
from app.schemas import ChangeBalance as ChangeBalanceSchema
from app.schemas import OperationField, CurrencyField # Enum
from app.schemas import Wallet as WalletSchema
from app.schemas import WalletCreate as WalletCreateSchema

from app.models.wallets import Wallet as WalletModel



router = APIRouter(prefix="/api/v1/wallets",
                   tags=["wallets"])




@router.post("/", response_model=WalletSchema, status_code=status.HTTP_201_CREATED)
async def create_wallet(wallet_data: WalletCreateSchema, db: AsyncSession = Depends(get_async_db)):
    """Создаение кошелька"""
    new_wallet = WalletModel(currency=wallet_data.currency,
                             balance=wallet_data.initial_balance)

    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)

    return new_wallet





@router.get("/{wallet_uuid}", response_model=WalletBalanceSchema, status_code=status.HTTP_200_OK)
async def get_balance(
        wallet_uuid: Annotated[UUID, Path(description="id_кошелька")],
        db: AsyncSession = Depends(get_async_db)):
    """Получение баланса"""
    stmt = select(WalletModel).where(WalletModel.id == wallet_uuid)
    wallet = await db.scalar(stmt)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Кошелек не найден")
    return wallet







@router.post("/{wallet_uuid}/operation", response_model=WalletBalanceSchema, status_code=status.HTTP_200_OK)
async def change_balance(
    wallet_uuid: Annotated[UUID, Path(description="id_кошелька")],
    operation: ChangeBalanceSchema,
    db: AsyncSession = Depends(get_async_db)):
    """Изменение баланса"""

    stmt = select(WalletModel).where(WalletModel.id == wallet_uuid).with_for_update()
    wallet = await db.scalar(stmt)

    if wallet is None:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кошелек не найден")

    if operation.operation_type == OperationField.DEPOSIT:
        wallet.balance += operation.amount
    else:
        if wallet.balance < operation.amount:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно средств на кошельке")
        wallet.balance -= operation.amount


    await db.commit()
    return wallet








