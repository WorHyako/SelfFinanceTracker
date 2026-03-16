from pathlib import Path
import json

from src.fetcher import MessageFetcher
from src.parser import MessageParser
from src.table_writer import TableWriter
from src.modifier import Modifier, TargetTypes

file_path = Path.cwd() / "settings.json"

try:
    settings = json.loads(file_path.read_text(encoding='utf-8'))
except (OSError, json.JSONDecodeError):
    exit(1)

message_fetcher = MessageFetcher(settings["FetcherPreset"]["db_path"])
messages = message_fetcher.fetch()

data_modifier = Modifier({
    TargetTypes.currency: settings["ModifierPreset"]["currency"],
    TargetTypes.amount_sign: settings["ModifierPreset"]["amount_sign"]
})
message_parser = MessageParser(
    settings["ParserPreset"]["contacts"],
    data_modifier)
parsed_messages = message_parser.parse(messages)
table_writer = TableWriter(
    doc_path=Path("./BankMessages.numbers")
)
table_writer.write(parsed_messages)
