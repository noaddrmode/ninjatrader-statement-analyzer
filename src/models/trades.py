from datetime import datetime
from pydantic import BaseModel
from typing import List, Tuple


class Trade(BaseModel):
    date_time: datetime
    filled_price: float
    buy_qty: int
    sell_qty: int
    code: str
    order_id: str


TradesList = List[Trade]
