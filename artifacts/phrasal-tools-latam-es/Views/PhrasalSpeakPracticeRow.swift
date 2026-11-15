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
    @State private var workTask: Task<Void, Never>?

    private enum Phase { case idle, speaking, listening, passed, failed }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Button {
                    startPractice()
                } label: {
                    Text(phase == .listening || phase == .speaking ? "…" : "Проговорить")
                        .font(.subheadline.weight(.semibold))
                        .frame(minWidth: 110, minHeight: 36)
                }
                .buttonStyle(.borderedProminent)
                .disabled(phase == .speaking || phase == .listening || en.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                if phase == .listening {
                    Button("Стоп") { capture.finish() }
                        .buttonStyle(.bordered)
                    Button("Отмена", role: .cancel) { cancel() }
                        .buttonStyle(.bordered)
                }
            }

            if phase == .speaking {
                Text("Слушай эталон…")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            } else if phase == .listening {
                Text(capture.partialText.isEmpty ? "Повтори вслух…" : capture.partialText)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.primary)
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

    private func startPractice() {
        workTask?.cancel()
        capture.cancel()
        speaker?.stop()
        heard = ""
        matchNote = ""
        phase = .speaking
        if speaker == nil { speaker = SpeechSpeaker(settings: settings) }
        speaker?.updateSettings(settings)

        workTask = Task { @MainActor in
            await speakENAwait(en)
            guard !Task.isCancelled else { return }
            phase = .listening
            try? await Task.sleep(nanoseconds: 250_000_000)
            try? AudioSessionManager.configureForRecording()
            var hints = PhraseSimilarity.sttVariants(for: en)
            hints.append(contentsOf: en.split(separator: " ").map(String.init))
            let target = en
            let text = await capture.captureUntilStopped(
                localeId: settings.rememberLocale.rawValue,
                maxSeconds: 45,
                contextualStrings: hints,
                autoFinishWhen: { PhraseSimilarity.passes(recognized: $0, expected: target) }
            )
            guard !Task.isCancelled else { return }
            evaluate(text, expected: target)
        }
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
            var resumed = false
            let finish = {
                guard !resumed else { return }
                resumed = true
                cont.resume()
            }
            speaker?.speakEN(text) { finish() }
            Task { @MainActor in
                try? await Task.sleep(nanoseconds: 8_000_000_000)
                finish()
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
