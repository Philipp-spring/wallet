import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool


from app.main import app
from app.database import Base
from app.db_depends import get_async_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL,
                                  connect_args={"check_same_thread": False},
                                  poolclass=StaticPool)


# Фабрика сессий
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)



async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_db] = override_get_db



@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Фикстура для создания таблиц"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)




@pytest_asyncio.fixture
async def client():
    """Фикстура для HTTP-клиента"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as as_client:
        yield as_client




# ---ТЕСТЫ---

@pytest.mark.asyncio # говорит pytest, что это асинхронный тест
async def test_create_wallet(client): # client - фикстура клиента
    """Проверяем создание кошелька"""
    response = await client.post("/api/v1/wallets/", json={"currency": "RUB", "initial_balance": 100})
    assert response.status_code == 201
    assert "id" in response.json()




@pytest.mark.asyncio
async def test_get_balance(client):
    """Проверяем получение баланса"""
    create_resp = await client.post("/api/v1/wallets/", json={"currency": "USD", "initial_balance": 50})
    wallet_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == "50.00"



# изменение баланса
@pytest.mark.asyncio
async def test_deposit(client):
    """Проверяем пополнение баланса"""
    create_resp = await client.post("/api/v1/wallets/", json={"currency": "EUR", "initial_balance": 10})
    wallet_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "DEPOSIT", "amount": 5})
    assert response.status_code == 200
    assert response.json()["balance"] == "15.00"



@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(client):
    """Проверяем ошибку при нехватке средств"""
    create_resp = await client.post("/api/v1/wallets/", json={"currency": "RUB", "initial_balance": 10})
    wallet_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 100})
    assert response.status_code == 400
    assert "Недостаточно средств" in response.json()["detail"]







