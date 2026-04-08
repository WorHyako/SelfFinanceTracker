# SelfFinanceTracker

```json
{
  "ParserPreset": {
    "contacts": [
      "contact1",
      "contact2"
    ]
  },
  "ModifierPreset": {
    "currency": "USD",
    "amount_sign": "+"
  },
  "FetcherPreset": {
    "db_path": "./chat.db"
  },
  "TablePreset": {
    "table_name": "Table 1",
    "sheet_name": "Sheet 1",
    "apple_scripts": {
      "parser": [
        "applescripts/table_parser.applescript"
      ],
      "writer": [
        "applescripts/row_filler.applescript"
      ]
    }
  }
}
```