from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
import requests
import json
from dataclasses import dataclass

from src.models import ParsedMessage


class TargetTypes(Enum):
    currency = auto()
    date = auto()
    amount_sign = auto()
    categories = auto()
    subcategory = auto()


@dataclass(slots=True)
class ExchangeRateCache:
    cache_file: Path
    _rates: dict[str, dict[str, float]]

    def __init__(self, cache_name: str) -> None:
        self.cache_file = Path.cwd() / cache_name
        self._rates = {}
        self.load()

    @staticmethod
    def _make_rate_key(from_currency: str,
                       to_currency: str) -> str:
        return f'{from_currency}|{to_currency}'

    def set(self,
            date: str,
            from_currency: str,
            to_currency: str,
            rate: float) -> None:
        rate_key = self._make_rate_key(from_currency, to_currency)
        if date not in self._rates:
            self._rates[date] = {}

        self._rates[date][rate_key] = float(rate)

    def get(self,
            date: str,
            from_currency: str,
            to_currency: str) -> float | None:
        if date not in self._rates:
            return None
        rate_key = self._make_rate_key(from_currency, to_currency)
        return self._rates[date].get(rate_key)

    def save(self) -> None:
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(sorted(self._rates.items()))
        self.cache_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8')

    def load(self) -> None:
        if not self.cache_file.exists():
            self._rates = {}

        try:
            raw_text = self.cache_file.read_text(encoding='utf-8')
            raw = json.loads(raw_text)
        except (OSError, json.JSONDecodeError):
            self._rates = {}
            return

        if not isinstance(raw, dict):
            self._rates = {}
            return

        normalized: dict[str, dict[str, float]] = {}
        for date_key, value in raw.items():
            if not isinstance(date_key, str) and not isinstance(value, dict):
                continue

            inner: dict[str, float] = {}
            for rate_kay, rate_value in value.items():
                if isinstance(rate_kay, str) and isinstance(rate_value, float):
                    inner[rate_kay] = float(rate_value)

            if inner:
                normalized[date_key] = inner

        self._rates = normalized


class Modifier:
    _default_types: dict[TargetTypes, str]
    _rate_cache: ExchangeRateCache

    def __init__(self, default_types: dict[TargetTypes, str]) -> None:
        self._default_types: dict[TargetTypes, str] = default_types
        self._rate_cache: ExchangeRateCache = ExchangeRateCache("rate_cache.json")

    @staticmethod
    def _normalize_date(date_time: datetime) -> str:
        return date_time.strftime("%Y-%m-%d")

    def _get_exchange_rate_at(self,
                              from_currency: str,
                              to_currency: str,
                              date_time: datetime) -> float:
        if date_time < datetime(2024, 3, 2):
            date_time = datetime(2024, 3, 2)

        norm_date = self._normalize_date(date_time)
        exchange_rate = self._rate_cache.get(norm_date,
                                             from_currency,
                                             to_currency)
        if exchange_rate is not None:
            return exchange_rate

        request_date = date_time
        while exchange_rate is None:
            url = (
                f"https://cdn.jsdelivr.net/npm/@fawazahmed0/"
                f"currency-api@{self._normalize_date(request_date)}/v1/"
                f"currencies/{from_currency}.json"
            )

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except requests.HTTPError:
                request_date -= timedelta(days=1)
                print(f'trying find rate at {request_date.strftime("%Y-%m-%d")}')
                continue

            data = response.json()
            exchange_rate = data[from_currency][to_currency]

        self._rate_cache.set(
            date=norm_date,
            from_currency=from_currency,
            to_currency=to_currency,
            rate=exchange_rate)
        self.save_rate_cache()

        return exchange_rate

    def save_rate_cache(self):
        self._rate_cache.save()

    def modify(self, value: ParsedMessage) -> ParsedMessage:
        date_time = value.operation_date
        to_currency = str(self._default_types[TargetTypes.currency]).upper()

        if value.amount_currency != to_currency or value.balance_currency != to_currency:
            exchange_rate = self._get_exchange_rate_at(
                date_time=date_time,
                from_currency=str(value.amount_currency).lower(),
                to_currency=str(to_currency).lower())
            if value.amount_currency != to_currency:
                value.amount = value.amount * exchange_rate
            if to_currency != value.balance_currency:
                value.balance = value.balance * exchange_rate

        if to_currency.upper() == "USD":
            to_currency = "US$"
        elif to_currency.upper() == "EUR":
            to_currency = "€"

        value.amount_currency = to_currency.upper()
        value.balance_currency = to_currency.upper()

        if self._default_types[TargetTypes.amount_sign] == '-':
            if value.amount > 0:
                value.amount = -value.amount
        else:
            if value.amount < 0:
                value.amount = -value.amount

        return value
