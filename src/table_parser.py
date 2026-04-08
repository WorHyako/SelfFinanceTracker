import applescript
from pathlib import Path
from dataclasses import dataclass
import json
from enum import Enum
from typing import Any
import datetime
import re


def to_iso_date(date: str) -> datetime.date | None:
    s = str(date)
    pattern = re.compile(
        r'^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+'
        r'(\d{1,2})\s+'
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+'
        r'(\d{4})\s+at\s+'
        r'(\d{2}):(\d{2}):(\d{2})$')

    month_map: dict[str, str] = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12",
    }

    m = pattern.match(s)
    date: datetime.date | None = None
    if m:
        day, month_name, year, hh, mm, ss = m.groups()
        iso = f"{year}-{month_map[month_name]}-{int(day):02d} {hh}:{mm}:{ss}"
        date = datetime.datetime.strptime(iso, "%Y-%m-%d %H:%M:%S")
    else:
        print(f"Error on parsing the date: {s}")
    return date


class RowValues(Enum):
    DATE = 0
    AMOUNT = 1
    CATEGORY = 2
    SUBCATEGORY = 3
    MERCHANT = 4


@dataclass(slots=True)
class TableCell:
    value: Any


@dataclass(slots=True)
class TableRow:
    row_idx: int
    values: dict[RowValues, TableCell]

    def __init__(self, row: dict[RowValues, Any], row_idx: int = -1):
        self.row_idx = row_idx
        self.values = row

    def as_list(self) -> list[Any]:
        return [self.values[RowValues.DATE],
                self.values[RowValues.AMOUNT],
                self.values[RowValues.MERCHANT]]

    def amount(self) -> float:
        amount: str = self.values[RowValues.AMOUNT].value
        amount_dig: float = float(amount.split(" ")[0].replace(",", "."))
        return round(amount_dig, 4)

    def amount_currency(self) -> str:
        amount: str = self.values[RowValues.AMOUNT].value
        amount_cur: str = amount.strip(" ")[1]
        return amount_cur

    def category(self) -> str:
        return self.values[RowValues.CATEGORY].value

    def merchant(self) -> str:
        return self.values[RowValues.MERCHANT].value

    def date(self) -> datetime.date:
        return self.values[RowValues.DATE].value


@dataclass(slots=True)
class TableParser:
    doc_path: Path
    sheet_name: str
    table_name: str
    script_str: list[str]
    target_row: int
    _apple_scripts: dict[str, str] | None

    def __init__(self,
                 doc_path: Path,
                 table_name: str = "Table 1",
                 sheet_name: str = "Sheet 1",
                 apple_scripts: list[Path] = None) -> None:
        self.doc_path: Path = doc_path
        self.sheet_name: str = sheet_name
        self.table_name: str = table_name
        self.script_str: list[str] = []
        self.target_row: int = -1
        self._load_apple_scripts(apple_scripts)

    def _load_apple_scripts(self, paths: list[Path] = None) -> None:
        if not paths:
            paths = []
        self._apple_scripts = {}
        for str_path in paths:
            path: Path = Path(str_path)
            with open(path, 'r') as f:
                raw_apple_script = f.read()
                self._apple_scripts[path.stem] = raw_apple_script
        return None

    def parse(self) -> list[TableRow] | None:
        print("Reading current table for existing rows...")
        self.script_str.append(self._apple_scripts["table_parser"])

        script = "\n".join(self.script_str)

        self.script_str.clear()

        result = applescript.run(script)
        if result.code != 0:
            print(f"Failed to run reading script:\n{result.err}")
            return None

        try:
            test = json.loads(result.out)
        except json.JSONDecodeError:
            print(f"Failed to parse json due table reading:\n{result.out}")
            return None

        rows = test.get("rows")
        out: list[TableRow] = []
        for item in rows:
            amount = item["values"][RowValues.AMOUNT.value].replace(",", ".")
            try:
                float(amount)
            except ValueError:
                print(f"Failed to parse amount as float: {amount}")
                continue
            amount = f"{amount} US$"
            merchant = item["values"][RowValues.MERCHANT.value]
            date = item["values"][RowValues.DATE.value]
            iso_date: datetime.date | None = to_iso_date(date)
            if iso_date is None:
                print(f"Failed to parse date as datetime: {date}")
                continue

            row: dict[RowValues, Any] = {
                RowValues.DATE: TableCell(iso_date),
                RowValues.AMOUNT: TableCell(amount),
                RowValues.MERCHANT: TableCell(merchant)
            }
            out.append(TableRow(row, item["row_index"]))

        return out
