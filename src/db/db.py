import configparser
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, String, DateTime

config = configparser.ConfigParser()
config.read(Path("config.ini"))
print(config.get("database", "url"))
DB_URL = config.get("database", "url", fallback="sqlite:///trades.db")


class Base(DeclarativeBase):
    pass


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    buy_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    sell_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    filled_price: Mapped[float] = mapped_column(Float, nullable=False)
    order_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Trade(id={self.id!r}, date_time={self.date_time!r}, filled_price={self.filled_price!r},\n"
            f"      buy_qty={self.buy_qty!r}, sell_qty={self.sell_qty!r}, order_id={self.order_id!r},\n"
            f"      code={self.code!r})"
        )


engine = create_engine(DB_URL)
Trade.metadata.create_all(engine)
