import SwiftUI

/// Home «On site» → CEFR level menu (A1…C2), then phrasals / phrases / sentences for that level only.
struct OnSiteMenuView: View {
    var body: some View {
        List {
            Section {
                Text("Фразовые глаголы, фразы и короткие предложения по уровню CEFR. Внутри уровня — только этот уровень, без выше.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Section("Уровень") {
                ForEach(CEFRLevel.allCases) { level in
                    let c = OnSiteCEFRStore.counts(level: level)
                    NavigationLink {
                        OnSiteLevelDetailView(level: level)
                    } label: {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(level.titleRU)
                                .font(.headline)
                            Text(level.blurbRU)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Text("\(c.phrasal) phrasal · \(c.phrase) фраз · \(c.sentence) предл.")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.tertiary)
                        }
                        .padding(.vertical, 2)
                    }
                }
            }
        }
        .navigationTitle("On site")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct OnSiteLevelDetailView: View {
    let level: CEFRLevel
    @Environment(AppSettings.self) private var settings
    @State private var speaker: SpeechSpeaker?
    @State private var kind: OnSiteContentKind = .phrasal

    private var rows: [OnSiteCEFRItem] {
        OnSiteCEFRStore.items(level: level, kind: kind)
    }

    var body: some View {
        List {
            Section {
                Text(level.blurbRU)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Picker("Тип", selection: $kind) {
                    ForEach(OnSiteContentKind.allCases) { k in
                        Text(k.titleRU).tag(k)
                    }
                }
                .pickerStyle(.segmented)
            }

            if rows.isEmpty {
                Section {
                    Text("Пока пусто для \(level.rawValue) · \(kind.titleRU).")
                        .foregroundStyle(.secondary)
                }
            } else {
                Section("\(kind.titleRU) · \(level.rawValue) · \(rows.count)") {
                    ForEach(rows) { item in
                        row(item)
                    }
                }
            }
        }
        .navigationTitle(level.rawValue)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { speaker = SpeechSpeaker(settings: settings) }
        .onDisappear { speaker?.stop() }
    }

    private func row(_ item: OnSiteCEFRItem) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(item.en)
                .font(.headline.weight(.bold))
            if !item.ru.isEmpty {
                Text(item.ru)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            if !item.exampleEn.isEmpty {
                Text(item.exampleEn)
                    .font(.caption)
                    .foregroundStyle(.tertiary)
            }
            if !item.exampleRu.isEmpty {
                Text(item.exampleRu)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
            Button {
                speaker?.updateSettings(settings)
                speaker?.speakEN(item.exampleEn.isEmpty ? item.en : item.exampleEn)
            } label: {
                Label("Слушать EN", systemImage: "speaker.wave.2.fill")
            }
            .buttonStyle(.bordered)
            .font(.subheadline.weight(.semibold))
        }
        .padding(.vertical, 4)
    }
}
