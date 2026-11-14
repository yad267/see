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
    @State private var expandedEN: String?

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
                .onChange(of: kind) { _, _ in expandedEN = nil }
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
        let expanded = expandedEN == item.en
        let usage = kind == .phrasal ? PhrasalUsageExamplesStore.examples(for: item.en) : []
        return VStack(alignment: .leading, spacing: 6) {
            Button {
                if kind == .phrasal {
                    expandedEN = expanded ? nil : item.en
                }
            } label: {
                HStack(alignment: .firstTextBaseline) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(item.en)
                            .font(.headline.weight(.bold))
                        if !item.ru.isEmpty {
                            Text(item.ru)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                    }
                    Spacer(minLength: 8)
                    if kind == .phrasal, !usage.isEmpty {
                        Image(systemName: expanded ? "chevron.up" : "chevron.down")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(.tertiary)
                    }
                }
            }
            .buttonStyle(.plain)

            if !expanded, !item.exampleEn.isEmpty {
                Text(item.exampleEn)
                    .font(.caption)
                    .foregroundStyle(.tertiary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            if expanded {
                if !usage.isEmpty {
                    Text("Примеры · обычный и на объекте")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(.secondary)
                    ForEach(Array(usage.enumerated()), id: \.offset) { _, ex in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(ex.contextTitleRU)
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.tertiary)
                            Text(ex.en)
                                .font(.caption.weight(.semibold))
                                .fixedSize(horizontal: false, vertical: true)
                            if !ex.ru.isEmpty {
                                Text(ex.ru)
                                    .font(.caption2)
                                    .foregroundStyle(.secondary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .padding(.top, 2)
                    }
                } else if !item.exampleEn.isEmpty {
                    Text(item.exampleEn)
                        .font(.caption)
                        .foregroundStyle(.tertiary)
                        .fixedSize(horizontal: false, vertical: true)
                    if !item.exampleRu.isEmpty {
                        Text(item.exampleRu)
                            .font(.caption2)
                            .foregroundStyle(.tertiary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }

            Button {
                speaker?.updateSettings(settings)
                let speak: String
                if expanded, let first = usage.first {
                    speak = first.en
                } else {
                    speak = item.exampleEn.isEmpty ? item.en : item.exampleEn
                }
                speaker?.speakEN(speak)
            } label: {
                Label("Слушать EN", systemImage: "speaker.wave.2.fill")
            }
            .buttonStyle(.bordered)
            .font(.subheadline.weight(.semibold))
        }
        .padding(.vertical, 4)
    }
}
