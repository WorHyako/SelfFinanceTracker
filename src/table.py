import datetime
from dataclasses import dataclass
from pathlib import Path
import json

from src.models import ParsedMessage
from src.table_parser import TableParser, TableRow, TableCell, RowValues
from src.table_writer import TableWriter


@dataclass(slots=True)
class Table:
    _table_writer: TableWriter
    _table_parser: TableParser
    _table_data: list[TableRow] | None

    def __init__(self):
        file_path = Path.cwd() / "settings.json"
        try:
            settings = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            exit(1)

        self._table_parser = TableParser(
            doc_path=Path("./BankMessages.numbers"),
            sheet_name=settings["TablePreset"]["sheet_name"],
            table_name=settings["TablePreset"]["table_name"],
            apple_scripts=settings["TablePreset"]["apple_scripts"]["parser"])

        self._table_writer = TableWriter(
            doc_path=Path("./BankMessages.numbers"),
            sheet_name=settings["TablePreset"]["sheet_name"],
            table_name=settings["TablePreset"]["table_name"],
            apple_scripts=settings["TablePreset"]["apple_scripts"]["writer"])
        self._table_data = []

    def sync(self) -> None:
        self._table_data = self._table_parser.parse()

    def write(self, messages: list[ParsedMessage]) -> None:
        print("Filtering rows...")
        rows: list[TableRow] = self._form_rows(messages)
        if not rows:
            return

        print("Writing rows...")
        self._table_writer.write(rows)

    def is_row_in_table(self, row: TableRow) -> bool:
        if row is None or not self._table_data:
            return False

        new_date = row.date()
        new_amount = row.amount()
        new_merchant = row.merchant()
        fields_to_compare = (new_date, new_amount, new_merchant)
        for existing_row in self._table_data:
            exs_date = existing_row.date()
            exs_amount = existing_row.amount()
            exs_merchant = existing_row.merchant()
            if fields_to_compare == (exs_date, exs_amount, exs_merchant):
                return True

        return False

    def _form_rows(self, messages: list[ParsedMessage]) -> list[TableRow]:
        formed_rows: list[TableRow] = []

        for message in messages:
            amount: str = f"{message.amount} {message.amount_currency}"
            merchant = message.merchant
            date: datetime.date = message.operation_date

            row: TableRow = TableRow({
                RowValues.DATE: TableCell(date),
                RowValues.AMOUNT: TableCell(amount),
                RowValues.MERCHANT: TableCell(merchant)
            })

            if self.is_row_in_table(row):
                continue

            formed_rows.append(row)

        return formed_rows
