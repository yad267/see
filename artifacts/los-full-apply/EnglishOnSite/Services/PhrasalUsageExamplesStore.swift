import Foundation

struct PhrasalUsageExample: Hashable, Codable {
    let en: String
    let ru: String
    /// `everyday` | `onsite`
    let context: String

    var contextTitleRU: String {
        switch context.lowercased() {
        case "onsite", "site", "on_site": return "На объекте"
        default: return "Обычный"
        }
    }
}

/// Bundled 2–3 usage sentences per phrasal (everyday + on-site).
enum PhrasalUsageExamplesStore {
    private struct Pack: Codable {
        let version: Int?
        let items: [String: Entry]
    }

    private struct Entry: Codable {
        let ru: String?
        let examples: [PhrasalUsageExample]
    }

    private static var cached: [String: [PhrasalUsageExample]]?

    private static func load() -> [String: [PhrasalUsageExample]] {
        if let cached { return cached }
        guard let url = Bundle.main.url(forResource: "phrasal_usage_examples_v1", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let pack = try? JSONDecoder().decode(Pack.self, from: data) else {
            cached = [:]
            return [:]
        }
        var map: [String: [PhrasalUsageExample]] = [:]
        for (key, entry) in pack.items {
            let k = key.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            let ex = entry.examples.filter {
                !$0.en.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            }
            if !ex.isEmpty { map[k] = Array(ex.prefix(3)) }
        }
        cached = map
        return map
    }

    static func examples(for en: String) -> [PhrasalUsageExample] {
        let key = en.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !key.isEmpty else { return [] }
        return load()[key] ?? []
    }
}
