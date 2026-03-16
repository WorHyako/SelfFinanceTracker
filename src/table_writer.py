import applescript
from pathlib import Path
from dataclasses import dataclass

from src.models import ParsedMessage


@dataclass(slots=True)
class TableWriter:
    doc_path: Path
    sheet_name: str
    table_name: str
    script_str: list[str]
    target_row: int

    def __init__(self,
                 doc_path: Path,
                 table_name: str = "Table 1",
                 sheet_name: str = "Sheet 1") -> None:
        self.doc_path: Path = doc_path
        self.sheet_name: str = sheet_name
        self.table_name: str = table_name
        self.script_str: list[str] = []
        self.target_row: int = -1

    def _get_start_row_idx(self) -> int:
        self._open_sheet()
            # repeat with i from 2 to maxRows
            # 	if value of cell ("A" & i) is missing value then
            # 		return i
            # 	end if
            # end repeat

        self.script_str.append(f'''
            set maxRows to row count
            return maxRows + 1
            ''')
        self._close_sheet()
        script = "\n".join(self.script_str)
        self.script_str.clear()
        result = applescript.run(script)
        last_row = int(result.out)
        return last_row

    def _add_row(self, message: ParsedMessage) -> None:
        amount = str(message.amount).replace('.', ',')

        self.script_str.append(f'''
            set amountValue to "{amount} {message.amount_currency}"
            set dateValue to "{message.operation_date}"
            set merchantValue to "{message.merchant}"
            
			set foundDateCell to first item of (every cell of range ("A2:A" & maxRows) whose (formatted value) is dateValue)
            if foundDateCell is missing value then
    			set foundMerchantCell to first item of (every cell of range ("A2:A" & maxRows) whose (formatted value) is merchantValue)
                if foundMerchantCell is missing value then
                    log "Row {{dataValue, amountValue, _, _, merchantValue}} will be written"
                    add row below row {self.target_row - 1}
                    set rowRange to range "A{self.target_row}:E{self.target_row}"
                else
                    log "Row {{dataValue, amountValue, _, _, merchantValue}} exists already"
                end if
                
                set newValues to {{dataValue, amountValue, _, _, merchantValue}}
                set value of cells of rowRange to newValues
            else
				log "Row {{dataValue, amountValue, _, _, merchantValue}} exists already"
            end if
            ''')
        # self.script_str.append(f'''
        #     tell cell ("A" & {self.target_row})
        #         set value to "dateValue"
        #         set format to date and time
        #     end tell
        #     tell cell ("E" & {self.target_row})
        #         set value to "merchantValue"
        #         set format to text
        #     end tell
        #     tell cell ("B" & {self.target_row})
        #         set value to "{amount} {message.amount_currency}"
        #         set format to currency
        #     end tell
        #     ''')
        self.target_row += 1

    def _open_sheet(self) -> None:
        self.script_str.append(
            f'''
            tell application "Numbers"
                tell front document
                    tell table "{self.table_name}" of sheet "{self.sheet_name}"
            ''')

    def _close_sheet(self) -> None:
        self.script_str.append(
            '''
                    end tell
                end tell
            end tell
            ''')

    def write(self, messages: list[ParsedMessage]) -> None:
        self.target_row = self._get_start_row_idx()

        self._open_sheet()
        # self.script_str.append(
        #     f'''
        #     set rowsToAdd to {len(messages)}
        #     repeat rowsToAdd times
        #         add row below last row
        #     end repeat
        #     ''')

        idx: int = 1
        max_idx: int = len(messages)
        self.script_str.append('''
			set maxRows to row count
        ''')
        for message in messages:
            print(f"preparing {idx}/{max_idx} message")
            self._add_row(message)
            idx += 1
        self._close_sheet()

        script = '\n'.join(self.script_str)
        self.script_str.clear()
        result = applescript.run(script)
        print(result.err)
        return result
