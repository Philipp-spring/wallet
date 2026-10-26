from fastapi import FastAPI
from app.routers import wallets



app = FastAPI(title="wallet",
              version="0.1.0")


app.include_router(wallets.router)


@app.get("/")
async def welcome() -> dict:
    """Корневой маршрут"""
    return {"message": "Кошелёк"}



