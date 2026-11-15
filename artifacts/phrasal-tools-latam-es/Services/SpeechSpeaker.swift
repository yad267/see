import Foundation

/// Public TTS façade for Translate / Library / Remember mini-lesson.
/// Prefers ElevenLabs; falls back to AVSpeech with visible status.
@MainActor
final class SpeechSpeaker {
    private var settings: AppSettings
    private var queue: [(String, Bool)] = []
    private var onFinished: (() -> Void)?
    private var onFirstStarted: (() -> Void)?
    private var active = false
    private var runTask: Task<Void, Never>?

    /// Short status for UI («системный голос» / «EL ошибка: HTTP …»).
    private(set) var statusNote: String = ""

    init(settings: AppSettings) {
        self.settings = settings
    }

    func updateSettings(_ settings: AppSettings) {
        self.settings = settings
    }

    func stop() {
        active = false
        queue.removeAll()
        onFinished = nil
        onFirstStarted = nil
        runTask?.cancel()
        runTask = nil
        ElevenLabsTTS.shared.stop()
    }

    func speakSequence(
        _ parts: [(text: String, english: Bool)],
        onFirstStarted: (() -> Void)? = nil,
        then finished: (() -> Void)? = nil
    ) {
        stop()
        statusNote = ""
        queue = parts.map { ($0.text, $0.english) }
        self.onFirstStarted = onFirstStarted
        onFinished = finished
        active = true
        runTask = Task { @MainActor in
            await self.drainQueue()
        }
    }

    func speakEN(_ text: String, then finished: (() -> Void)? = nil) {
        // Trailing closure must bind to `then` (not onStarted) — keep call-site compat.
        speakSequence([(text, true)], then: finished)
    }

    func speakRU(_ text: String, then finished: (() -> Void)? = nil) {
        speakSequence([(text, false)], then: finished)
    }

    /// Latin American Spanish via ElevenLabs (same key/model/cache path as EN).
    func speakES(_ text: String, then finished: (() -> Void)? = nil) {
        stop()
        statusNote = ""
        onFinished = finished
        active = true
        runTask = Task { @MainActor in
            await ElevenLabsTTS.shared.speak(
                text: text,
                lang: .es,
                settings: self.settings,
                onPlaybackStarted: nil
            )
            self.statusNote = ElevenLabsTTS.shared.lastStatusRU
            let done = self.onFinished
            self.onFinished = nil
            self.active = false
            done?()
        }
    }

    func speak(
        text: String,
        lang: SiteVoiceLang,
        then finished: (() -> Void)? = nil
    ) {
        switch lang {
        case .en: speakEN(text, then: finished)
        case .ru: speakRU(text, then: finished)
        case .es: speakES(text, then: finished)
        }
    }

    private func drainQueue() async {
        var first = true
        while active, !queue.isEmpty {
            let (text, isEN) = queue.removeFirst()
            let lang: SiteVoiceLang = isEN ? .en : .ru
            let started = first ? onFirstStarted : nil
            first = false
            await ElevenLabsTTS.shared.speak(
                text: text,
                lang: lang,
                settings: settings,
                onPlaybackStarted: started
            )
            if Task.isCancelled || !active { break }
            statusNote = ElevenLabsTTS.shared.lastStatusRU
        }
        onFirstStarted = nil
        let done = onFinished
        onFinished = nil
        active = false
        done?()
    }
}
