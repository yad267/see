import Foundation

struct PhrasalToolsPack: Codable {
    var schema: Int
    var contentVersion: Int
    var title: String?
    var titleRu: String?
    var sections: [PhrasalToolsSection]

    enum CodingKeys: String, CodingKey {
        case schema
        case contentVersion = "content_version"
        case title
        case titleRu = "title_ru"
        case sections
    }
}

struct PhrasalToolsSection: Codable, Identifiable, Hashable {
    let id: String
    let order: Int?
    let titleEn: String
    let titleRu: String
    let items: [PhrasalToolItem]

    enum CodingKeys: String, CodingKey {
        case id, order, items
        case titleEn = "title_en"
        case titleRu = "title_ru"
    }
}

struct PhrasalToolItem: Codable, Identifiable, Hashable {
    let id: String
    let phrasal: String
    let en: String
    let ru: String
    let tool: String?

    var speakText: String { en }
}

/// Bundle loader for `phrasal_tools.json` (not lessons_pack).
enum PhrasalToolsStore {
    private static var cached: PhrasalToolsPack?

    static func pack() -> PhrasalToolsPack {
        if let cached { return cached }
        guard let url = Bundle.main.url(forResource: "phrasal_tools", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode(PhrasalToolsPack.self, from: data)
        else {
            return PhrasalToolsPack(schema: 1, contentVersion: 0, title: nil, titleRu: nil, sections: [])
        }
        cached = decoded
        return decoded
    }

    static func sections() -> [PhrasalToolsSection] {
        pack().sections.sorted { ($0.order ?? 0) < ($1.order ?? 0) }
    }
}
