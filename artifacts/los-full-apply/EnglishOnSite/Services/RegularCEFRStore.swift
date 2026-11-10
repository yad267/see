import Foundation

enum RegularContentKind: String, CaseIterable, Identifiable, Hashable {
    case phrasal
    case phrase
    case dialogue

    var id: String { rawValue }

    var titleRU: String {
        switch self {
        case .phrasal: return "Фразовые глаголы"
        case .phrase: return "Лёгкие фразы"
        case .dialogue: return "Диалоги"
        }
    }

    var blurbRU: String {
        switch self {
        case .phrasal: return "Обычный EN · get / take / look… по уровням A1–C2"
        case .phrase: return "Короткие фразы от простых к сложным"
        case .dialogue: return "Сцены и запрос темы → до 10 диалогов"
        }
    }

    var systemImage: String {
        switch self {
        case .phrasal: return "arrow.left.arrow.right"
        case .phrase: return "text.bubble"
        case .dialogue: return "person.2.wave.2"
        }
    }
}

struct RegularCEFRItem: Identifiable, Hashable, Codable {
    var id: String { "\(kind.rawValue)|\(cefr.rawValue)|\(en.lowercased())" }
    let kind: RegularContentKind
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

enum RegularCEFRStore {
    private struct Pack: Codable {
        let version: Int?
        let items: [RegularCEFRItem]
    }

    private static var cached: [RegularCEFRItem]?

    static func all() -> [RegularCEFRItem] {
        if let cached { return cached }
        guard let url = Bundle.main.url(forResource: "regular_cefr_pack_v1", withExtension: "json"),
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

    /// Exact level only — never higher.
    static func items(kind: RegularContentKind, level: CEFRLevel) -> [RegularCEFRItem] {
        all().filter { $0.kind == kind && $0.cefr == level }
    }

    static func count(kind: RegularContentKind, level: CEFRLevel) -> Int {
        items(kind: kind, level: level).count
    }

    static func counts(kind: RegularContentKind) -> [(CEFRLevel, Int)] {
        CEFRLevel.allCases.map { ($0, count(kind: kind, level: $0)) }
    }
}
