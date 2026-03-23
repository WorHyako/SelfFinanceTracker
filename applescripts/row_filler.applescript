script RowFiller
    on writeRow(tableName, sheetName, dateValue, amountValue, merchantValue)
        tell application "Numbers" to tell table tableName of sheet sheetName of front document
            set maxRows to row count
            set newValues to {dateValue, amountValue, missing value, missing value, merchantValue}
            set hasDate to exists (first cell of range ("A2:A" & maxRows) whose (formatted value) is dateValue)
            set hasMerchant to exists (first cell of range ("E2:E" & maxRows) whose (formatted value) is merchantValue)

            if (not hasDate) and (not hasMerchant) then
                add row below last row
                set rowRange to last row

                set value of cell 1 of rowRange to dateValue
                set value of cell 2 of rowRange to amountValue
                set value of cell 3 of rowRange to missing value
                set value of cell 4 of rowRange to missing value
                set value of cell 5 of rowRange to merchantValue

                log "Row " & newValues & " written"
            else
                log "Row " & newValues & " exists already"
            end if
        end tell
    end writeRow
end script
