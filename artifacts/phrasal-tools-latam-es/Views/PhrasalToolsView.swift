import SwiftUI

/// Sections of tool-context phrasals: select → list → Проговорить / В тренажёр.
struct PhrasalToolsView: View {
    @State private var selectedSectionIds: Set<String> = []
    @State private var toast = ""
    @State private var goTrainer = false

    private var sections: [PhrasalToolsSection] { PhrasalToolsStore.sections() }

    private var selectedItems: [PhrasalToolItem] {
        sections
            .filter { selectedSectionIds.contains($0.id) }
            .flatMap(\.items)
    }

    var body: some View {
        List {
            Section {
                Text("Выбери секции (по 10 фраз). В списке — проговорить или сохранить в тренажёр.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                NavigationLink("Открыть тренажёр") {
                    PhrasalTrainerView()
                }
            }

            Section("Секции") {
                if sections.isEmpty {
                    Text("Нет phrasal_tools.json в Resources.")
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(sections) { section in
                        Button {
                            toggle(section.id)
                        } label: {
                            HStack(alignment: .top, spacing: 10) {
                                Image(systemName: selectedSectionIds.contains(section.id) ? "checkmark.square.fill" : "square")
                                    .foregroundStyle(selectedSectionIds.contains(section.id) ? Color.accentColor : .secondary)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(section.titleRu)
                                        .font(.body.weight(.semibold))
                                        .foregroundStyle(.primary)
                                    Text("\(section.titleEn) · \(section.items.count)")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                Spacer(minLength: 0)
                            }
                        }
                        .buttonStyle(.plain)
                    }
                    if !sections.isEmpty {
                        HStack {
                            Button("Все") {
                                selectedSectionIds = Set(sections.map(\.id))
                            }
                            Button("Сброс") { selectedSectionIds = [] }
                        }
                        .font(.subheadline.weight(.semibold))
                    }
                }
            }

            if !selectedItems.isEmpty {
                Section("Выбрано · \(selectedItems.count)") {
                    ForEach(selectedItems) { item in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(item.en)
                                .font(.body.weight(.semibold))
                            Text(item.ru)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                            if !item.phrasal.isEmpty {
                                Text(item.phrasal)
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(.tertiary)
                            }
                            PhrasalSpeakPracticeControls(en: item.en, ru: item.ru)
                            Button {
                                let added = PhrasalTrainerStore.add(.fromToolItem(item))
                                toast = added ? "В тренажёре" : "Уже в тренажёре"
                            } label: {
                                Text(PhrasalTrainerStore.contains(en: item.en) ? "В тренажёре ✓" : "В тренажёр")
                                    .font(.subheadline.weight(.semibold))
                                    .frame(minWidth: 110, minHeight: 36)
                            }
                            .buttonStyle(.bordered)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }

            if !toast.isEmpty {
                Section {
                    Text(toast).font(.caption).foregroundStyle(.secondary)
                }
            }
        }
        .navigationTitle("Инструменты")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(isPresented: $goTrainer) {
            PhrasalTrainerView()
        }
    }

    private func toggle(_ id: String) {
        if selectedSectionIds.contains(id) {
            selectedSectionIds.remove(id)
        } else {
            selectedSectionIds.insert(id)
        }
    }
}
