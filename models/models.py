from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, MetaData, Table, TIMESTAMP, Boolean, Double

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("hashed_password", String, nullable=False),
    Column("balance", Double, nullable=False, default=0),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)

tokentable = Table(
    "tokentable",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("access_token", String, nullable=False),
    Column("owner_id", Integer, ForeignKey("user.id"))
)

stock = Table(
    "stock",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("image", String),
    Column("price", Double, nullable=False),
    Column("company", String, nullable=False),
    Column("ticker", String),
    Column("description", String)
)

personal_stocks = Table(
    "personal_stocks",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("quantity", Integer),
    Column("owner_id", Integer, ForeignKey("user.id")),
    Column("stock_id", Integer, ForeignKey("stock.id"))
)
