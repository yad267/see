import Foundation

/// Top-level app track: site vs general everyday English.
enum AppLearningMode: String, CaseIterable, Identifiable, Hashable {
    case onSite
    case regular

    var id: String { rawValue }

    var title: String {
        switch self {
        case .onSite: return "Language on Site"
        case .regular: return "Regular Language"
        }
    }

    var blurbRU: String {
        switch self {
        case .onSite:
            return "Объект Ireland · On site · CEFR A1–C2"
        case .regular:
            return "Обычный EN · скажи/напиши тему → до 10 диалогов"
        }
    }
}
