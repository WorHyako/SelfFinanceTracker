script RowFiller
    on writeRow(tableName, sheetName, dateValue, amountValue, merchantValue)
        tell application "Numbers" to tell table tableName of sheet sheetName of front document
            add row below last row
            set rowRange to last row
            set value of cell 1 of rowRange to dateValue
            set value of cell 2 of rowRange to amountValue
            set value of cell 3 of rowRange to missing value
            set value of cell 4 of rowRange to missing value
            set value of cell 5 of rowRange to merchantValue
        end tell
    end writeRow
end script
