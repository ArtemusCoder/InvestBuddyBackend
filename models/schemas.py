from datetime import datetime

from pydantic import BaseModel


class StockCreate(BaseModel):
    id: int
    price: int
    company: str
