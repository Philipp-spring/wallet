from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum




class CurrencyField(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"

class WalletCreate(BaseModel):
    currency: CurrencyField = Field(..., description="тип валюты")
    initial_balance: Decimal = Field(...,
                                     ge=0,
                                     max_digits=12,
                                     decimal_places=2,
                                     description="первоначальный баланс")



class Wallet(BaseModel):
    id: UUID = Field(..., description="uuid кошелька")
    currency: CurrencyField = Field(..., description="тип валюты")
    balance: Decimal = Field(..., ge=0, description="баланс")

    model_config = ConfigDict(from_attributes=True)



# возвращает ТОЛЬКО баланс
class WalletBalance(BaseModel):
    balance: Decimal = Field(..., ge=0, description="баланс")

    model_config = ConfigDict(from_attributes=True)




class OperationField(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class ChangeBalance(BaseModel):
    operation_type: OperationField = Field(...,
                                           description="тип операции: 'DEPOSIT' / 'WITHDRAW'")
    amount: Decimal = Field(...,
                            gt=0,
                            max_digits=12,
                            decimal_places=2,
                            description="сумма пополнения/снятия")

