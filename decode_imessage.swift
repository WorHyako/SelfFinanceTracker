import Foundation

func decodeAttributedBody(_ data: Data) -> String? {
    if let attributed = try? NSKeyedUnarchiver.unarchivedObject(
        ofClass: NSAttributedString.self,
        from: data) {
        return attributed.string
    }

    if let mutableAttributed = try? NSKeyedUnarchiver.unarchivedObject(
        ofClass: NSMutableAttributedString.self,
        from: data) {
        return mutableAttributed.string
    }

    if let s = String(data: data, encoding: .utf8), !s.isEmpty {
        return s
    }

    return nil
}

let input = FileHandle.standardInput.readDataToEndOfFile()

if let result = decodeAttributedBody(input) {
    print(result)
    exit(0)
} else {
    exit(1)
}