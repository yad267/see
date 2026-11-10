import SwiftUI

/// Shared «Проговорить» control: TTS → user repeats → STT → word-overlap check.
struct PhrasalSpeakPracticeControls: View {
    @Environment(AppSettings.self) private var settings

    let en: String
    let ru: String

    @State private var speaker: SpeechSpeaker?
    @State private var capture = TimedSpeechCapture()
    @State private var phase: Phase = .idle
    @State private var heard = ""
    @State private var matchNote = ""
    @State private var ttsNote = ""
    @State private var workTask: Task<Void, Never>?

    private enum Phase { case idle, speaking, listening, passed, failed }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Button {
                    startPractice()
                } label: {
                    Text(phaseLabel)
                        .font(.subheadline.weight(.semibold))
                        .frame(minWidth: 110, minHeight: 36)
                }
                .buttonStyle(.borderedProminent)
                .disabled(phase == .speaking || phase == .listening || en.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                Button {
                    listenOnly()
                } label: {
                    Text("▶ Слушать")
                        .font(.subheadline.weight(.semibold))
                        .frame(minHeight: 36)
                }
                .buttonStyle(.bordered)
                .disabled(phase == .speaking || phase == .listening || en.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                if phase == .listening {
                    Button("Стоп") { capture.finish() }
                        .buttonStyle(.bordered)
                    Button("Отмена", role: .cancel) { cancel() }
                        .buttonStyle(.bordered)
                }
            }

            if phase == .speaking {
                Text(ttsNote.isEmpty ? "Слушай эталон…" : ttsNote)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            } else if phase == .listening {
                Text(capture.partialText.isEmpty ? "Повтори вслух…" : capture.partialText)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(capture.partialText.isEmpty ? .secondary : .primary)
            } else if phase == .passed {
                Text(matchNote.isEmpty ? "Верно" : "Верно · \(matchNote)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.green)
            } else if phase == .failed {
                Text(matchNote.isEmpty ? "Неверно" : "Неверно · \(matchNote)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.orange)
                if !heard.isEmpty {
                    Text("Слышал: \(heard)")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .onAppear {
            if speaker == nil { speaker = SpeechSpeaker(settings: settings) }
        }
        .onDisappear {
            cancel()
            speaker?.stop()
        }
    }

    private var phaseLabel: String {
        switch phase {
        case .speaking: return "…"
        case .listening: return "…"
        default: return "Проговорить"
        }
    }

    private func listenOnly() {
        workTask?.cancel()
        capture.cancel()
        heard = ""
        matchNote = ""
        ttsNote = ""
        phase = .speaking
        if speaker == nil { speaker = SpeechSpeaker(settings: settings) }
        speaker?.updateSettings(settings)
        workTask = Task { @MainActor in
            await speakENAwait(en)
            guard !Task.isCancelled else { return }
            phase = .idle
            if !ttsNote.isEmpty {
                // keep note briefly if TTS fell back / failed
                try? await Task.sleep(nanoseconds: 1_200_000_000)
                if phase == .idle { ttsNote = "" }
            }
        }
    }

    private func startPractice() {
        workTask?.cancel()
        capture.cancel()
        speaker?.stop()
        heard = ""
        matchNote = ""
        ttsNote = ""
        phase = .speaking
        if speaker == nil { speaker = SpeechSpeaker(settings: settings) }
        speaker?.updateSettings(settings)

        workTask = Task { @MainActor in
            await speakENAwait(en)
            guard !Task.isCancelled else { return }

            // Clean handoff: stop TTS engine, release session, then open mic.
            speaker?.stop()
            AudioSessionManager.deactivate()
            try? await Task.sleep(nanoseconds: 450_000_000)
            try? AudioSessionManager.configureForRecording()
            try? await Task.sleep(nanoseconds: 200_000_000)

            phase = .listening
            var hints = PhraseSimilarity.sttVariants(for: en)
            hints.append(contentsOf: en.split(separator: " ").map(String.init))
            let target = en
            // Always EN locale for English phrases (rememberLocale is en-IE, keep explicit).
            let locale = englishLocaleId()
            let text = await capture.captureUntilStopped(
                localeId: locale,
                maxSeconds: 45,
                contextualStrings: hints,
                autoFinishWhen: { PhraseSimilarity.passes(recognized: $0, expected: target) }
            )
            guard !Task.isCancelled else { return }
            evaluate(text, expected: target)
        }
    }

    private func englishLocaleId() -> String {
        let remembered = settings.rememberLocale.rawValue
        if remembered.lowercased().hasPrefix("en") { return remembered }
        return "en-IE"
    }

    private func evaluate(_ raw: String, expected: String) {
        heard = PhraseSimilarity.displayAgainstTarget(raw, expected: expected)
        let hit = wordHits(recognized: heard.isEmpty ? raw : heard, expected: expected)
        let total = max(wordTokens(expected).count, 1)
        let pct = PhraseSimilarity.percent(recognized: heard.isEmpty ? raw : heard, expected: expected)
        matchNote = "\(hit)/\(total) слов · \(pct)%"
        if PhraseSimilarity.passes(recognized: raw, expected: expected) || Double(hit) / Double(total) >= 0.75 {
            phase = .passed
        } else {
            phase = .failed
        }
    }

    private func speakENAwait(_ text: String) async {
        await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
            final class Gate: @unchecked Sendable {
                var done = false
                func fire(_ body: () -> Void) {
                    guard !done else { return }
                    done = true
                    body()
                }
            }
            let gate = Gate()
            speaker?.speakEN(text) {
                gate.fire { cont.resume() }
            }
            // Safety cap — long enough for typical site phrases; status shown if EL slow.
            Task { @MainActor in
                try? await Task.sleep(nanoseconds: 12_000_000_000)
                if let note = speaker?.statusNote, !note.isEmpty {
                    ttsNote = note
                }
                gate.fire { cont.resume() }
            }
        }
        await MainActor.run {
            if let note = speaker?.statusNote, !note.isEmpty {
                ttsNote = note
            }
        }
    }

    private func cancel() {
        workTask?.cancel()
        workTask = nil
        capture.cancel()
        speaker?.stop()
        phase = .idle
        matchNote = ""
        heard = ""
        ttsNote = ""
    }

    private func wordTokens(_ text: String) -> [String] {
        text
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
    }

    private func wordHits(recognized: String, expected: String) -> Int {
        let got = Set(wordTokens(recognized))
        return wordTokens(expected).filter { got.contains($0) }.count
    }
}
