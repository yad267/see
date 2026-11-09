import Foundation

/// Normalizes and scores spoken STT against a roleplay script line.
/// Threshold: 75% content-word overlap (articles/prepositions forgiven).
enum DialogueFuzzyMatcher {
    static let passThreshold: Double = 0.75

    private static let stopWords: Set<String> = [
        "a", "an", "the", "to", "of", "in", "on", "at", "for", "and", "or",
        "is", "are", "be", "been", "am", "i", "you", "we", "it", "this", "that",
        "with", "from", "as", "by", "up", "out", "if", "so", "do", "does", "did"
    ]

    struct Score {
        let percentage: Double
        var passes: Bool { percentage >= DialogueFuzzyMatcher.passThreshold }
    }

    static func normalize(_ raw: String) -> String {
        let lowered = raw.lowercased()
        let allowed = CharacterSet.alphanumerics.union(.whitespaces)
        let filtered = String(lowered.unicodeScalars.map { allowed.contains($0) ? Character($0) : " " })
        return filtered
            .split(whereSeparator: \.isWhitespace)
            .joined(separator: " ")
    }

    static func tokens(_ raw: String, stripStopWords: Bool) -> [String] {
        let parts = normalize(raw).split(separator: " ").map(String.init)
        guard stripStopWords else { return parts }
        let content = parts.filter { !stopWords.contains($0) && $0.count > 1 }
        // If everything was stop-words, fall back to all tokens
        return content.isEmpty ? parts : content
    }

    /// Word-overlap F1-style score with light Levenshtein forgiveness for near-misses.
    static func score(transcript: String, expected: String) -> Score {
        let spoken = tokens(transcript, stripStopWords: true)
        let target = tokens(expected, stripStopWords: true)

        guard !target.isEmpty else {
            return Score(percentage: spoken.isEmpty ? 1 : 0)
        }
        guard !spoken.isEmpty else {
            return Score(percentage: 0)
        }

        var matched = 0
        var used = Set<Int>()
        for t in target {
            if let idx = spoken.enumerated().first(where: { !used.contains($0.offset) && softEqual($0.element, t) })?.offset {
                used.insert(idx)
                matched += 1
            }
        }

        let recall = Double(matched) / Double(target.count)
        let precision = Double(matched) / Double(spoken.count)
        let f1 = (precision + recall) == 0 ? 0 : (2 * precision * recall) / (precision + recall)
        return Score(percentage: min(1, max(0, f1)))
    }

    private static func softEqual(_ a: String, _ b: String) -> Bool {
        if a == b { return true }
        // Allow small typos on longer technical words
        guard a.count >= 4, b.count >= 4 else { return false }
        return levenshtein(a, b) <= max(1, min(a.count, b.count) / 5)
    }

    private static func levenshtein(_ a: String, _ b: String) -> Int {
        let a = Array(a), b = Array(b)
        var prev = Array(0...b.count)
        var cur = Array(repeating: 0, count: b.count + 1)
        for i in 1...a.count {
            cur[0] = i
            for j in 1...b.count {
                let cost = a[i - 1] == b[j - 1] ? 0 : 1
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            }
            prev = cur
        }
        return prev[b.count]
    }
}
