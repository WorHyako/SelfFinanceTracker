set firstRow to true
set out to "{\"rows\":["

tell application "Numbers" to tell table "Table 1" of sheet "Sheet 1" of front document
	set rc to row count
	set cc to column count
	repeat with r from 1 to rc
		if firstRow then
			set firstRow to false
		else
			set out to out & ","
		end if
		set out to out & "{\"row_index\":" & (r as text) & ",\"values\":["
		repeat with c from 1 to cc
			set cellValue to value of cell c of row r
			set out to out & "\"" & (cellValue as text) & "\""
			if c is not cc then set out to out & ","
		end repeat
		set out to out & "]}"
	end repeat
end tell

set out to out & "]}"
return out