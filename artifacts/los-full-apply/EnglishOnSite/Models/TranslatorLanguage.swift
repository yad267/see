import Foundation

/// Translator UI languages (one-tap). Gemini prompt uses `geminiName` / `rawValue`.
enum TranslatorLanguage: String, CaseIterable, Identifiable, Hashable {
    case en
    case ru
    case es

    var id: String { rawValue }

    var shortLabel: String {
        switch self {
        case .en: return "EN"
        case .ru: return "RU"
        case .es: return "ES"
        }
    }

    var titleRU: String {
        switch self {
        case .en: return "English"
        case .ru: return "Русский"
        case .es: return "Español"
        }
    }

    /// Speech recognition locale for mic (ES = LatAm / Mexican, not Castilian).
    var micLocaleId: String {
        switch self {
        case .en: return "en-IE"
        case .ru: return "ru-RU"
        case .es: return "es-MX"
        }
    }

    var geminiName: String {
        switch self {
        case .en: return "English"
        case .ru: return "Russian"
        case .es: return "Spanish"
        }
    }

    var siteVoiceLang: SiteVoiceLang {
        switch self {
        case .en: return .en
        case .ru: return .ru
        case .es: return .es
        }
    }
}
