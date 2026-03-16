import re
import datetime
from dataclasses import dataclass

from src.models import RawMessage, ParsedMessage
from src.modifier import Modifier

@dataclass(slots=True)
class MessageParser:
    MESSAGE_PATTERN = re.compile(
        r'"(?P<merchant>[^"]+)",\s*'
        r'(?P<amount>-?\d+(?:\.\d+)?),\s*'
        r'(?P<currency>[A-Z]{3}),\s*'
        r'"(?P<datetime>\d{2}-\d{2}-\d{4} \d{2}:\d{2})"'
    )

    contacts: list[str]
    modifier: Modifier

    def __init__(self, contacts: list[str], modifier: Modifier) -> None:
        self.contacts = [c.lower() for c in contacts]
        self.modifier = modifier

    def parse(self, messages: list[RawMessage]) -> list[ParsedMessage]:
        parsed: list[ParsedMessage] = []

        for message in messages:
            if not self._is_contact_match(message.user_id):
                continue
            match = self.MESSAGE_PATTERN.search(message.text)
            if not match:
                continue
            parsed_message = ParsedMessage(
                merchant=match.group('merchant'),
                amount=float(match.group('amount')),
                amount_currency=match.group('currency'),
                balance=float(0),
                balance_currency="",
                operation_date=datetime.datetime.strptime(match.group('datetime'), '%d-%m-%Y %H:%M')
            )

            modified_message = self.modifier.modify(parsed_message)
            parsed.append(modified_message)
        return parsed if len(parsed) > 0 else None

    def _is_contact_match(self, user_id: str) -> bool:
        lu = user_id.lower()
        return any(contact in lu for contact in self.contacts)
