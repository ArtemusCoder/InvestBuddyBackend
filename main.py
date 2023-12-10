from fastapi_users import fastapi_users, FastAPIUsers
from pydantic import BaseModel, Field
from sqlalchemy import insert, select
from fastapi import FastAPI, Request, status, Depends, HTTPException
from auth.database import get_async_session

from models.models import stock
from models.schemas import StockCreate

from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="InvestBuddy App"
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


async def get_enabled_backends(request: Request):
    return [auth_backend]


current_user = fastapi_users.current_user(get_enabled_backends=get_enabled_backends)


@app.get("/user")
async def user(user: User = Depends(current_user)):
    return user


@app.get("/stocks")
async def stocks(user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(stock)
        result = await session.execute(query)
        result = result.all()
        return {
            "status": "success",
            "data": result,
            "details": None
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@app.post("/stock/add")
async def add_stock(new_operation: StockCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(stock).values(**new_operation.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}
