import Foundation

enum CEFRLevel: String, CaseIterable, Identifiable, Hashable {
    case a1 = "A1"
    case a2 = "A2"
    case b1 = "B1"
    case b2 = "B2"
    case c1 = "C1"
    case c2 = "C2"

    var id: String { rawValue }

    var titleRU: String {
        switch self {
        case .a1: return "A1 · старт"
        case .a2: return "A2 · база на объекте"
        case .b1: return "B1 · увереннее"
        case .b2: return "B2 · сложнее"
        case .c1: return "C1 · продвинутый"
        case .c2: return "C2 · почти носитель"
        }
    }

    var blurbRU: String {
        switch self {
        case .a1: return "Только A1 — без уровней выше"
        case .a2: return "Только A2 — без B/C"
        case .b1: return "Только B1 — без B2/C"
        case .b2: return "Только B2 — без C"
        case .c1: return "Только C1 — без C2"
        case .c2: return "Только C2"
        }
    }
}

enum OnSiteContentKind: String, CaseIterable, Identifiable, Hashable {
    case phrasal
    case phrase
    case sentence

    var id: String { rawValue }

    var titleRU: String {
        switch self {
        case .phrasal: return "Фразовые глаголы"
        case .phrase: return "Фразы"
        case .sentence: return "Короткие предложения"
        }
    }
}

struct OnSiteCEFRItem: Identifiable, Hashable, Codable {
    var id: String { "\(kind.rawValue)|\(cefr.rawValue)|\(en.lowercased())" }
    let kind: OnSiteContentKind
    let cefr: CEFRLevel
    let en: String
    let ru: String
    let exampleEn: String
    let exampleRu: String

    enum CodingKeys: String, CodingKey {
        case kind, cefr, en, ru
        case exampleEn = "example_en"
        case exampleRu = "example_ru"
    }
}

/// Bundled On site menu bank: phrasals / phrases / light sentences by exact CEFR level.
enum OnSiteCEFRStore {
    private struct Pack: Codable {
        let version: Int?
        let items: [OnSiteCEFRItem]
    }

    private static var cached: [OnSiteCEFRItem]?

    static func all() -> [OnSiteCEFRItem] {
        if let cached { return cached }
        guard let url = Bundle.main.url(forResource: "onsite_cefr_pack_v1", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let pack = try? JSONDecoder().decode(Pack.self, from: data) else {
            cached = []
            return []
        }
        cached = pack.items.filter {
            !$0.en.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        }
        return cached!
    }

    /// Strict: only this level — never higher, never lower band spill.
    static func items(level: CEFRLevel, kind: OnSiteContentKind? = nil) -> [OnSiteCEFRItem] {
        all().filter { item in
            item.cefr == level && (kind == nil || item.kind == kind)
        }
    }

    static func counts(level: CEFRLevel) -> (phrasal: Int, phrase: Int, sentence: Int) {
        (
            items(level: level, kind: .phrasal).count,
            items(level: level, kind: .phrase).count,
            items(level: level, kind: .sentence).count
        )
    }
}
