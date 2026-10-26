import uuid
from sqlalchemy import UUID # инструмент для создания полей в БД с типом UUID (используется только в моделях SQLAlchemy)
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal


from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False)
    currency: Mapped[str] = mapped_column(server_default="RUB", nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2),
                                             default=Decimal("0.00"),
                                             server_default="0.00",
                                             nullable=False)
