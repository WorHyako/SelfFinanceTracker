from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class RawMessage:
    user_id: str
    text: str
    date: str = ""
    service: str = ""
    account: str = ""
    is_from_me: bool = False


@dataclass(slots=True)
class ParsedMessage:
    amount: float
    amount_currency: str
    merchant: str
    operation_date: datetime
    balance: float
    balance_currency: str
