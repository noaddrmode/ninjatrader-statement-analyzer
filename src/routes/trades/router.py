from fastapi import APIRouter
from models.trades import TradesList


from datetime import datetime
from db.statements import StatementProcessor
from db.db import engine as DatabaseEngine


router = APIRouter(prefix="/trades")


@router.get("/")
async def index(start: datetime | None = None, end: datetime | None = None) -> TradesList:
    trades = []
    processor = StatementProcessor(DatabaseEngine)
    if start and end:
        # Example param
        # start_date = "2025-02-02T00:00:00"
        trades = processor.get_trades_between(start, end)
    else:
        trades = processor.get_all_trades()
    return trades
