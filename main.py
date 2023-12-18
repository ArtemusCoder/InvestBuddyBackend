from fastapi.encoders import jsonable_encoder
from fastapi_users import fastapi_users, FastAPIUsers
from pydantic import BaseModel, Field
from sqlalchemy import insert, select, update, delete
from fastapi import FastAPI, Request, status, Depends, HTTPException
from auth.database import get_async_session

from models.models import stock, user, personal_stocks
from models.schemas import StockCreate

from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="InvestBuddy App"
)

app.mount("/images", StaticFiles(directory="images"), name='images')

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
async def user_data(user: User = Depends(current_user)):
    return user


@app.post("/balance/add/{money}")
async def balance_add(money: float, curr_user: User = Depends(current_user),
                      session: AsyncSession = Depends(get_async_session)):
    try:
        query = update(User).where(User.id == curr_user.id).values(balance=(curr_user.balance + money))
        result = await session.execute(query)
        await session.commit()
        return {"status": "success", "data": result}
    except Exception as e:
        print(e)
        return {"status": "error"}


@app.get("/stocks")
async def stocks(user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(stock)
        result = await session.execute(query)
        output = []
        for i, stock_elem in enumerate(result.all()):
            output.append(dict())
            output[i]["id"] = stock_elem[0]
            output[i]["price"] = stock_elem[2]
            output[i]["company"] = stock_elem[3]
            output[i]["ticket"] = stock_elem[4]
            output[i]["description"] = stock_elem[5]
            output[i]["image"] = stock_elem[1]
        return jsonable_encoder(output)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@app.get("/stock/{id}")
async def stock_detail(id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(stock).where(stock.c.id == id)
        result = await session.execute(query)
        result = result.first()
        print(result)
        output = {"id": result[0], "price": result[2], "company": result[3], "ticket": result[4],
                  "description": result[5], "image": result[1]}
        return jsonable_encoder(output)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@app.post("/stock/add")
async def add_stock(new_operation: StockCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(stock).values(**new_operation)
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}


@app.post("/stock/buy/{id}")
async def buy_stock(id: int, quantity: int = 1, user: User = Depends(current_user),
                    session: AsyncSession = Depends(get_async_session)):
    query = select(stock).where(stock.c.id == id)
    stock_elem = await session.execute(query)
    stock_elem = stock_elem.first()
    if user.balance < (quantity * stock_elem[2]):
        return HTTPException(status_code=400, detail={
            "status": "error",
            "data": "Недостаточно средств",
            "details": None
        })
    else:
        query = select(personal_stocks).where(personal_stocks.c.stock_id == id)
        result = await session.execute(query)
        result = result.first()
        if result is not None:
            await session.execute(
                update(personal_stocks).where(personal_stocks.c.id == result[0]).values(quantity=(quantity + result[1])))
            await balance_add(-(stock_elem[2] * quantity), user, session)
            await session.commit()
        else:
            stock_buy = insert(personal_stocks).values(owner_id=user.id, stock_id=id, quantity=quantity)
            await balance_add(-(stock_elem[2] * quantity), user, session)
            await session.execute(stock_buy)
            await session.commit()
        return {"status": "success", "data": "Покупка удалась"}


@app.post("/stock/sell/{id}")
async def sell_stock(id: int, quantity: int, user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_async_session)):
    query = select(personal_stocks).where(personal_stocks.c.stock_id == id).where(personal_stocks.c.owner_id == user.id)
    result = await session.execute(query)
    result = result.first()
    if result is None:
        return HTTPException(status_code=400, detail={
            "status": "error",
            "data": "Таких акций нет",
            "details": None
        })
    if result[1] < quantity:
        return HTTPException(status_code=400, detail={
            "status": "error",
            "data": "У вас нет столько акций",
            "details": None
        })
    try:
        if result[1] - quantity == 0:
            await session.execute(delete(personal_stocks).where(personal_stocks.c.id == result[0]))
            await session.commit()
            stock_elem = await stock_detail(result[3], user, session)
            await balance_add(stock_elem["price"] * quantity, user, session)
        else:
            await session.execute(
                update(personal_stocks).where(personal_stocks.c.id == result[0]).values(
                    quantity=(result[1] - quantity)))
            await session.commit()
            stock_elem = await stock_detail(result[3], user, session)
            await balance_add(stock_elem["price"] * quantity, user, session)
        return {"status": "success"}
    except:
        return HTTPException(status_code=500, detail={
            "status": "error",
            "data": "У вас нет столько акций",
            "details": None
        })


@app.get("/my-stocks")
async def my_stocks(user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(personal_stocks).where(personal_stocks.c.owner_id == user.id)
        result = await session.execute(query)
        output = []
        for i, stock_elem in enumerate(result.all()):
            output.append(dict())
            stock_elem_detail = await stock_detail(stock_elem[3], user, session)
            output[i]["id"] = stock_elem_detail["id"]
            output[i]["price"] = stock_elem_detail["price"]
            output[i]["company"] = stock_elem_detail["company"]
            output[i]["ticket"] = stock_elem_detail["ticket"]
            output[i]["quantity"] = stock_elem[1]
            output[i]["image"] = stock_elem_detail["image"]
        return jsonable_encoder(output)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })
