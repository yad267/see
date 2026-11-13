import SwiftUI
import SwiftData

/// «Мои фразы» → Повтор: Да / Нет. Нет (и Да) озвучивают EN через TTS.
struct ReviewSessionView: View {
    let items: [LibraryItem]

    @Environment(AppSettings.self) private var settings
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss

    @State private var index = 0
    @State private var revealed = false
    @State private var speaker: SpeechSpeaker?
    @State private var statusNote = ""

    private var current: LibraryItem? {
        items.indices.contains(index) ? items[index] : nil
    }

    private var finished: Bool { index >= items.count }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if finished {
                Text("Готово")
                    .font(.title.weight(.bold))
                Text("Повтор: \(items.count) фраз.")
                    .foregroundStyle(.secondary)
                Button("Закрыть") { dismiss() }
                    .buttonStyle(.borderedProminent)
                Spacer()
            } else if let item = current {
                Text("\(index + 1) / \(items.count)")
                    .font(.headline)
                    .foregroundStyle(.secondary)

                // Prompt with RU first — EN after reveal / on Нет.
                Text(item.ru.isEmpty ? "…" : item.ru)
                    .font(.title2.weight(.semibold))

                if revealed {
                    Text(item.en)
                        .font(.title.weight(.bold))
                        .foregroundStyle(.primary)
                } else {
                    Text("EN скрыт — Да/Нет или «Показать»")
                        .font(.subheadline)
                        .foregroundStyle(.tertiary)
                }

                if !statusNote.isEmpty {
                    Text(statusNote)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                HStack(spacing: 12) {
                    Button("Показать") {
                        revealed = true
                        speakEN(item.en)
                    }
                    .buttonStyle(.bordered)

                    Button("Да") {
                        grade(known: true, item: item)
                    }
                    .buttonStyle(.borderedProminent)

                    Button("Нет") {
                        grade(known: false, item: item)
                    }
                    .buttonStyle(.bordered)
                    .tint(.orange)
                }
                .font(.headline)

                Spacer()
            }
        }
        .padding(20)
        .navigationTitle("Повтор")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            if speaker == nil {
                speaker = SpeechSpeaker(settings: settings)
            }
        }
        .onDisappear {
            speaker?.stop()
        }
    }

    private func grade(known: Bool, item: LibraryItem) {
        // Always hear the EN target on grade — especially «Нет».
        speakEN(item.en)
        revealed = true
        if known {
            LibraryStore.markLearned(item, context: modelContext)
        } else {
            LibraryStore.markReviewFailed(item, context: modelContext)
        }
        // Advance after a short beat so TTS can start.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
            revealed = false
            index += 1
            statusNote = ""
        }
    }

    private func speakEN(_ text: String) {
        let en = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !en.isEmpty else { return }
        if speaker == nil {
            speaker = SpeechSpeaker(settings: settings)
        }
        speaker?.updateSettings(settings)
        speaker?.stop()
        speaker?.speakEN(en) {
            statusNote = speaker?.statusNote ?? ""
        }
    }
}
