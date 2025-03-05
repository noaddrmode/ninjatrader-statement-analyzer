from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from db.db import Trade, engine as DatabaseEngine
from datetime import datetime


class StatementProcessor:
    def __init__(self, engine):
        try:
            self.Session = sessionmaker(engine)
        except SQLAlchemyError:
            raise

    def record_trades(self, trades):
        with self.Session() as session:
            try:
                for _ticker, trades in trades.items():
                    stmt = sqlite_insert(Trade).values(trades)
                    stmt = stmt.on_conflict_do_nothing()
                    session.execute(stmt)
            except SQLAlchemyError:
                session.rollback()
                raise
            else:
                session.commit()

    def get_all_trades(self, limit=None, offset=None):
        with self.Session() as session:
            try:
                query = (
                    select(Trade)
                    .order_by(Trade.date_time.desc())
                    .limit(limit)
                    .offset(offset)
                )
                res = session.execute(query).scalars().all()
                return res
            except SQLAlchemyError as e:
                raise

    def get_trades_between(self, datetime_start, datetime_end, limit=None, offset=None):
        with self.Session() as session:
            try:
                query = (
                    select(Trade)
                    .where(
                        Trade.date_time >= datetime_start,
                        Trade.date_time <= datetime_end,
                    )
                    .order_by(Trade.date_time.desc())
                    .limit(limit)
                    .offset(offset)
                )
                res = session.execute(query).scalars().all()
                return res
            except ValueError:
                raise
            except SQLAlchemyError:
                raise
