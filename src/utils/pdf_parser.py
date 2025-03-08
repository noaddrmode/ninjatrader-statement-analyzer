import configparser
import re
import pdfplumber
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from db.statements import StatementProcessor
from db.db import engine as DatabaseEngine

config = configparser.ConfigParser()
config.read(Path("config.ini"))
DB_URL = config.get("database", "url", fallback="sqlite:///trades.db")
STATEMENTS_FOLDER = config.get("statements", "dir", fallback="data/statements")


class PDFParser:
    def __init__(self, engine):
        try:
            self.db_helper = StatementProcessor(engine)
            self.data_dir = Path(STATEMENTS_FOLDER)
        except (SQLAlchemyError, ValueError):
            raise

    def get_pdfs(self):
        return sorted(self.data_dir.glob("**/*.pdf"))

    def extract_text_from_pdf(self, pdf):
        try:
            with pdfplumber.open(pdf) as file:
                full_text = ""
                for page in file.pages:
                    text = page.extract_text(keep_blank_chars=True)
                    full_text = full_text + "\n\n" + text
                return full_text
        except Exception:
            raise

    def format_trade(self, symbol, trade):
        formatted = {
            "symbol": symbol,
            # todo, handle timezone (GMT)
            "date_time": datetime.strptime(trade[0], "%m/%d/%Y %I:%M:%S %p(GMT)"),
            "code": trade[1],
            "buy_qty": trade[2] if trade[2] != "-" else 0,
            "sell_qty": trade[3] if trade[3] != "-" else 0,
            "filled_price": trade[4],
            "order_id": trade[5],
        }
        return formatted

    ## Tables format ##
    # Trading details for Micro E-mini Nasdaq 100 - Mar. 2025 (MNQH5)
    # Date & Time                  Code    Buy Qty Sell Qty  Filled Price       Order_id
    # 02/21/2025 03:18:02 PM(GMT)  FILL          1        -       6112.25  1,332,755,394
    # 02/21/2025 03:20:02 PM(GMT)  FILL          -        1       6112.25  1,332,755,395
    # ...
    # Trading details for Micro E-mini S&P 500 - Mar. 2025 (MESH5)
    # Date & Time                  Code    Buy Qty Sell Qty  Filled Price       Order_id
    # ...
    def extract_trades_from_pdf(self, pdf):
        trades_by_symbol = defaultdict(list)
        text = self.extract_text_from_pdf(pdf)

        regex = {
            "table_title": re.compile(r"Trading details for .*?\((\w+)\)"),
            "trade_fills": re.compile(
                r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM)\(GMT\))"
                r"\s+(FILL)\s+(-|\d+)\s+(-|\d+)"
                r"\s+([\d.]+)\s+([\d,]+)"
            ),
        }
        title_matches = list(regex["table_title"].finditer(text))

        for i, match in enumerate(title_matches):
            symbol = match.group(1)  # MNQH5
            start_index = match.end()
            end_index = (
                title_matches[i + 1].start()
                if i + 1 < len(title_matches)
                else len(text)
            )
            trades = regex["trade_fills"].findall(text[start_index:end_index])
            trades_by_symbol[symbol] = [self.format_trade(symbol, trade) for trade in trades]
        return trades_by_symbol

    def get_all_trades(self):
        pdf_files = self.get_pdfs()
        all_trades = defaultdict(list)
        for pdf in pdf_files:
            try:
                trades = self.extract_trades_from_pdf(pdf)
                for symbol, trades in trades.items():
                    all_trades[symbol].extend(trades)
            except ValueError:
                continue
        return all_trades

    def store_trades_in_db(self, trades):
        try:
            self.db_helper.record_trades(trades)
        except SQLAlchemyError as e:
            raise e


if __name__ == "__main__":
    print("Debugging pdf_parser")
    parser = PDFParser(DatabaseEngine)
    trades = parser.get_all_trades()

    from pprint import pprint

    pprint(trades)
    parser.store_trades_in_db(trades)
