import Foundation

/// One phrase saved into the speak trainer (separate from lessons_pack / LearningBank).
struct PhrasalTrainerPhrase: Codable, Identifiable, Hashable {
    let id: String
    var en: String
    var ru: String
    var phrasal: String
    var source: String
    var createdAt: Date

    init(
        id: String = UUID().uuidString,
        en: String,
        ru: String,
        phrasal: String = "",
        source: String,
        createdAt: Date = Date()
    ) {
        self.id = id
        self.en = en
        self.ru = ru
        self.phrasal = phrasal
        self.source = source
        self.createdAt = createdAt
    }

    static func fromToolItem(_ item: PhrasalToolItem) -> PhrasalTrainerPhrase {
        PhrasalTrainerPhrase(
            id: "tool:\(item.id)",
            en: item.en,
            ru: item.ru,
            phrasal: item.phrasal,
            source: "phrasal_tools"
        )
    }
}

/// Documents/phrasal_trainer.json — user deck for TTS→STT practice.
@MainActor
enum PhrasalTrainerStore {
    private static let fileName = "phrasal_trainer.json"

    private struct Pack: Codable {
        var version: Int
        var items: [PhrasalTrainerPhrase]
    }

    private static var fileURL: URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        return docs.appendingPathComponent(fileName)
    }

    static func load() -> [PhrasalTrainerPhrase] {
        guard let data = try? Data(contentsOf: fileURL),
              let pack = try? JSONDecoder().decode(Pack.self, from: data)
        else { return [] }
        return pack.items.sorted { $0.createdAt > $1.createdAt }
    }

    @discardableResult
    static func save(_ items: [PhrasalTrainerPhrase]) -> Bool {
        let pack = Pack(version: 1, items: items)
        guard let data = try? JSONEncoder().encode(pack) else { return false }
        do {
            try data.write(to: fileURL, options: [.atomic])
            return true
        } catch {
            print("[phrasal-trainer] write failed: \(error)")
            return false
        }
    }

    /// Insert or refresh by id / normalized EN. Returns true if newly added.
    @discardableResult
    static func add(_ phrase: PhrasalTrainerPhrase) -> Bool {
        var items = load()
        let key = normalize(phrase.en)
        if let idx = items.firstIndex(where: { $0.id == phrase.id || normalize($0.en) == key }) {
            items[idx] = PhrasalTrainerPhrase(
                id: items[idx].id,
                en: phrase.en,
                ru: phrase.ru,
                phrasal: phrase.phrasal.isEmpty ? items[idx].phrasal : phrase.phrasal,
                source: phrase.source,
                createdAt: items[idx].createdAt
            )
            save(items)
            return false
        }
        items.insert(phrase, at: 0)
        save(items)
        return true
    }

    static func contains(en: String) -> Bool {
        let key = normalize(en)
        return load().contains { normalize($0.en) == key }
    }

    static func remove(id: String) {
        var items = load()
        items.removeAll { $0.id == id }
        save(items)
    }

    static func clear() {
        save([])
    }

    private static func normalize(_ text: String) -> String {
        text
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
    }
}
