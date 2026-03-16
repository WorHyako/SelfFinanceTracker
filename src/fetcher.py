from abc import abstractmethod, ABC
from pathlib import Path
from typing import override
from imessage_reader import fetch_data
from dataclasses import dataclass

from src.models import RawMessage

@dataclass(slots=True)
class IMessageFetcher(ABC):
    db_path: Path

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @abstractmethod
    def fetch(self) -> list[RawMessage]:
        pass


class MessageFetcher(IMessageFetcher):
    @override
    def fetch(self) -> list[RawMessage]:
        fd = fetch_data.FetchData(str(self.db_path))
        rows = fd.get_messages()

        result: list[RawMessage] = []
        for row in rows:
            user_id = "" if len(row) < 1 or row[0] is None else str(row[0])
            text = "[NO TEXT]" if len(row) < 2 or row[1] is None else str(row[1])
            date = "" if len(row) < 3 or row[2] is None else str(row[2])
            service = "" if len(row) < 4 or row[3] is None else str(row[3])
            account = "" if len(row) < 5 or row[4] is None else str(row[4])
            is_from_me = bool(row[5]) if len(row) > 5 else False

            result.append(
                RawMessage(
                    user_id=user_id,
                    text=text,
                    date=date,
                    service=service,
                    account=account,
                    is_from_me=is_from_me
                )
            )
        return result
