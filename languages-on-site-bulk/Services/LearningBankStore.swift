import Foundation
import SwiftData

struct LearningBankEntry: Identifiable, Hashable {
    var id: String { LibraryItem.normalizeEN(en) + "|" + type.rawValue }
    let en: String
    let ru: String
    let example: String
    let meta: String
    let type: LibraryItemType
}

/// Bundled words / site phrasals / sentences (from CSV → JSON). Progress lives in LibraryItem.
enum LearningBankStore {
    private static let phrasalSeedDayKey = "eos.learningBank.lastPhrasalSeedDay"

    private struct Pack: Codable {
        let version: Int?
        let items: [Row]
    }

    private struct Row: Codable {
        let en: String
        let ru: String?
        let example: String?
        let part_of_speech: String?
        let category: String?
    }

    static func words() -> [LearningBankEntry] {
        load(resource: "learning_words_v1", type: .word) { row in
            LearningBankEntry(
                en: row.en,
                ru: row.ru ?? "",
                example: row.example ?? "",
                meta: row.part_of_speech ?? "",
                type: .word
            )
        }
    }

    static func sitePhrasals() -> [LearningBankEntry] {
        load(resource: "learning_phrasals_site_v1", type: .phrasal) { row in
            LearningBankEntry(
                en: row.en,
                ru: row.ru ?? "",
                example: row.example ?? "",
                meta: row.category ?? "site",
                type: .phrasal
            )
        }
    }

    static func sentences() -> [LearningBankEntry] {
        load(resource: "learning_sentences_v1", type: .sentence) { row in
            LearningBankEntry(
                en: row.en,
                ru: row.ru ?? "",
                example: "",
                meta: row.category ?? "",
                type: .sentence
            )
        }
    }

    /// Dump phrasals into «Мои фразы» (dedupe by normalized EN). Returns how many new rows were inserted.
    @MainActor
    @discardableResult
    static func seedPhrasalsIntoLibrary(
        context: ModelContext,
        limit: Int? = nil
    ) -> Int {
        let bank = sitePhrasals()
        let slice: ArraySlice<LearningBankEntry>
        if let limit, limit > 0 {
            slice = bank.prefix(limit)
        } else {
            slice = bank[...]
        }
        var added = 0
        for entry in slice {
            let before = LibraryStore.find(normalizedKey: entry.en, context: context)
            let wasNew = before == nil
            _ = LibraryStore.add(
                context: context,
                source: .bank,
                en: entry.en,
                ru: entry.ru,
                tipRu: entry.example,
                tag: .other,
                itemType: .phrasal
            )
            if wasNew { added += 1 }
        }
        markPhrasalSeedToday()
        return added
    }

    /// Once per calendar day: add up to `dailyLimit` not-yet-in-library phrasals.
    @MainActor
    @discardableResult
    static func seedPhrasalsDailyIfNeeded(
        context: ModelContext,
        dailyLimit: Int = 20
    ) -> Int {
        guard !alreadySeededPhrasalsToday() else { return 0 }
        let existing = Set(
            (try? context.fetch(FetchDescriptor<LibraryItem>()))?
                .map { LibraryItem.normalizeEN($0.en) } ?? []
        )
        var added = 0
        for entry in sitePhrasals() {
            guard added < dailyLimit else { break }
            let key = LibraryItem.normalizeEN(entry.en)
            guard !key.isEmpty, !existing.contains(key) else { continue }
            _ = LibraryStore.add(
                context: context,
                source: .bank,
                en: entry.en,
                ru: entry.ru,
                tipRu: entry.example,
                tag: .other,
                itemType: .phrasal
            )
            added += 1
        }
        markPhrasalSeedToday()
        return added
    }

    static func alreadySeededPhrasalsToday() -> Bool {
        let today = Self.dayStamp(Date())
        return UserDefaults.standard.string(forKey: phrasalSeedDayKey) == today
    }

    private static func markPhrasalSeedToday() {
        UserDefaults.standard.set(dayStamp(Date()), forKey: phrasalSeedDayKey)
    }

    private static func dayStamp(_ date: Date) -> String {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = .current
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: date)
    }

    private static func load(
        resource: String,
        type: LibraryItemType,
        map: (Row) -> LearningBankEntry
    ) -> [LearningBankEntry] {
        guard let url = Bundle.main.url(forResource: resource, withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let pack = try? JSONDecoder().decode(Pack.self, from: data) else {
            return []
        }
        return pack.items
            .map(map)
            .filter { !$0.en.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }
}
