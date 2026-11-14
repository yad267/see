import SwiftUI

/// Regular Language hub: Phrasals · Light phrases · Dialogues — each with CEFR A1–C2.
struct RegularLanguageMenuView: View {
    var body: some View {
        List {
            Section {
                Text("Обычный английский для любого пользователя. Три раздела — в каждом уровни A1…C2 от простого к сложному.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Section("Разделы") {
                ForEach(RegularContentKind.allCases) { kind in
                    NavigationLink {
                        RegularKindLevelsView(kind: kind)
                    } label: {
                        Label {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(kind.titleRU).font(.headline)
                                Text(kind.blurbRU)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        } icon: {
                            Image(systemName: kind.systemImage)
                        }
                        .padding(.vertical, 2)
                    }
                }
            }
        }
        .navigationTitle("Regular Language")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct RegularKindLevelsView: View {
    let kind: RegularContentKind

    var body: some View {
        List {
            Section {
                Text("Только выбранный уровень — без выше. Порядок: A1 → C2 (от лёгкого к сложному).")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Section("Уровень · \(kind.titleRU)") {
                ForEach(CEFRLevel.allCases) { level in
                    let n = RegularCEFRStore.count(kind: kind, level: level)
                    NavigationLink {
                        RegularLevelDetailView(kind: kind, level: level)
                    } label: {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(level.titleRU).font(.headline)
                            Text(level.blurbRU)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Text("\(n) шт.")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.tertiary)
                        }
                        .padding(.vertical, 2)
                    }
                }
            }
        }
        .navigationTitle(kind.titleRU)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct RegularLevelDetailView: View {
    let kind: RegularContentKind
    let level: CEFRLevel

    @Environment(AppSettings.self) private var settings
    @State private var speaker: SpeechSpeaker?
    @State private var path = NavigationPath()
    @State private var expandedEN: String?

    private var rows: [RegularCEFRItem] {
        RegularCEFRStore.items(kind: kind, level: level)
    }

    var body: some View {
        List {
            Section {
                Text("\(kind.titleRU) · только \(level.rawValue)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            if kind == .dialogue {
                Section("Собрать диалоги") {
                    NavigationLink {
                        RegularLanguageRequestView(preferredLevel: level) { _ in }
                    } label: {
                        Label("Тема голосом или текстом · до 10 уроков (\(level.rawValue))", systemImage: "mic.badge.plus")
                    }
                    Text("Пример: dating dialogues — Gemini соберёт до 10 диалогов на этом уровне.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            if rows.isEmpty {
                Section {
                    Text("Пока пусто для \(level.rawValue).")
                        .foregroundStyle(.secondary)
                }
            } else {
                Section("\(rows.count)") {
                    ForEach(rows) { item in
                        row(item)
                    }
                }
            }
        }
        .navigationTitle("\(kind.titleRU) · \(level.rawValue)")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { speaker = SpeechSpeaker(settings: settings) }
        .onDisappear { speaker?.stop() }
    }

    private func row(_ item: RegularCEFRItem) -> some View {
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
                    Text("Примеры · обычный и быт / объект")
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
