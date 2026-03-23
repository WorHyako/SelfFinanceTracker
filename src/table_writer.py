import applescript
from pathlib import Path
from dataclasses import dataclass
import textwrap

from src import applescript_compiler
from src.models import ParsedMessage


@dataclass(slots=True)
class TableWriter:
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

    def _load_apple_scripts(self, paths: list[Path] = []) -> None:
        if paths is None:
            return None
        self._apple_scripts = {}
        for str_path in paths:
            path: Path = Path(str_path)
            with open(path, 'r') as f:
                raw_apple_script = f.read()
                self._apple_scripts[path.stem] = raw_apple_script
        return None

    def _get_start_row_idx(self) -> int:
        self._open_sheet()

        self._add_to_script(f'''
            set maxRows to row count
            return maxRows + 1
            ''')
        self._close_sheet()
        script = '\n'.join(self.script_str)
        self.script_str.clear()
        result = applescript.run(script)
        last_row = int(result.out)
        return last_row

    def _add_to_script(self, script: str) -> None:
        script = textwrap.dedent(script).strip()
        self.script_str.append(script.replace('\n\n', '\n'))

    def _add_row(self, message: ParsedMessage) -> None:
        amount = str(message.amount).replace('.', ',')

        self._add_to_script(f'''
            RowFiller's writeRow("{self.table_name}", "{self.sheet_name}", "{message.operation_date}", "{amount} {message.amount_currency}", "{message.merchant}")
            ''')

        # self._add_to_script(f'''
        #     set amountValue to "{amount} {message.amount_currency}"
        #     set dateValue to "{message.operation_date}"
        #     set merchantValue to "{message.merchant}"
        #     set newValues to {{dateValue, amountValue, missing value, missing value, merchantValue}}
        #
        #     set hasDate to exists (first cell of range ("A2:A" & maxRows) whose (formatted value) is dateValue)
        #     set hasMerchant to exists (first cell of range ("E2:E" & maxRows) whose (formatted value) is merchantValue)
        #
        #     if (not hasDate) and (not hasMerchant) then
        #         add row below row {self.target_row - 1}
        #         set rowRange to last row
        #         set value of cells of rowRange to newValues
        #         log "Row " & newValues & " written"
        #     else
        #         log "Row " & newValues & " exists already"
        #     end if
        #     ''')
        self.target_row += 1

    def _open_sheet(self) -> None:
        self._add_to_script(
            f'''
            tell application "Numbers" to tell table "{self.table_name}" of sheet "{self.sheet_name}" of front document
            ''')

    def _close_sheet(self) -> None:
        self._add_to_script(
            '''
            end tell
            ''')

    def write(self, messages: list[ParsedMessage]) -> None:
        self.target_row = self._get_start_row_idx()
        max_idx: int = len(messages)
        idx: int = 1

        self.script_str.append(self._apple_scripts['row_filler'])

        for message in messages:
            print(f"preparing {idx}/{max_idx} message")
            self._add_row(message)
            idx += 1

        script = '\n'.join(self.script_str)

        self.script_str.clear()

        script_file: Path = Path("./") / "applescripts" / "out_script.applescript"
        script_file.parent.mkdir(parents=True, exist_ok=True)
        script_file.write_text("", encoding="utf-8")

        with open(script_file, "w") as f:
            f.write(script)

        try:
            applescript_compiler.compile_applescript(script_file)
        except RuntimeError as error:
            print(f"Failed to compile applescript:\n{error}")
            print("Trying to run applescript without compilation")
            result = applescript.run(script)
            print(result.err)
