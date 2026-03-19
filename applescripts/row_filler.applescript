script RowFilter
    on writeRow(tableName, sheetName, targetRow, dateValue, amountValue, merchantValue)
        tell application "Numbers" to tell table tableName of sheet sheetName of front document
            set maxRows to row count
            set newValues to {{dateValue, amountValue, missing value, missing value, merchantValue}}
            set hasDate to exists (first cell of range ("A2:A" & maxRows) whose (formatted value) is dateValue)
            set hasMerchant to exists (first cell of range ("E2:E" & maxRows) whose (formatted value) is merchantValue)

            if (not hasDate) and (not hasMerchant) then
                add row below row targetRow - 1
                set rowRange to last row
                set value of cells of rowRange to newValues
                log "Row " & newValues & " written"
            else
                log "Row " & newValues & " exists already"
            end if
        end tell
    end writeRow
end script
