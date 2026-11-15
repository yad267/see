import SwiftUI

/// Saved phrasal/custom phrases deck: practice TTS→STT, add own RU via Gemini.
struct PhrasalTrainerView: View {
    @Environment(AppSettings.self) private var settings

    @State private var items: [PhrasalTrainerPhrase] = []
    @State private var showAddOwn = false
    @State private var ownRU = ""
    @State private var addNote = ""
    @State private var isTranslating = false
    @State private var practiceAll = false
    @State private var practiceIndex = 0
    @State private var toast = ""

    var body: some View {
        List {
            Section {
                Button {
                    ownRU = ""
                    addNote = ""
                    showAddOwn = true
                } label: {
                    Label("Добавить свою", systemImage: "plus.bubble")
                        .font(.headline)
                        .frame(maxWidth: .infinity, minHeight: 44)
                }
                .disabled(isTranslating)

                if !items.isEmpty {
                    Button {
                        practiceAll = true
                        practiceIndex = 0
                    } label: {
                        Label("Гонять все (\(items.count))", systemImage: "mic.fill")
                            .font(.subheadline.weight(.semibold))
                    }
                }

                if !toast.isEmpty {
                    Text(toast).font(.caption).foregroundStyle(.secondary)
                }
            }

            if items.isEmpty {
                Section {
                    Text("Пусто. Добавь фразы из «Инструменты» или свою на русском.")
                        .foregroundStyle(.secondary)
                }
            } else {
                Section("Тренажёр · \(items.count)") {
                    ForEach(items) { item in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(item.en)
                                .font(.body.weight(.semibold))
                            if !item.ru.isEmpty {
                                Text(item.ru)
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            }
                            if !item.phrasal.isEmpty {
                                Text(item.phrasal)
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(.tertiary)
                            }
                            PhrasalSpeakPracticeControls(en: item.en, ru: item.ru)
                            Button(role: .destructive) {
                                PhrasalTrainerStore.remove(id: item.id)
                                reload()
                            } label: {
                                Text("Убрать")
                                    .font(.caption.weight(.semibold))
                            }
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
        }
        .navigationTitle("Тренажёр")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { reload() }
        .sheet(isPresented: $showAddOwn) { addOwnSheet }
        .navigationDestination(isPresented: $practiceAll) {
            PhrasalTrainerDrillView(
                phrases: items,
                startIndex: practiceIndex
            )
        }
    }

    private var addOwnSheet: some View {
        NavigationStack {
            Form {
                Section("Фраза на русском") {
                    TextField("Например: передай мне дрель", text: $ownRU, axis: .vertical)
                        .lineLimit(2...5)
                }
                if !addNote.isEmpty {
                    Section {
                        Text(addNote)
                            .font(.footnote)
                            .foregroundStyle(addNote.contains("добавлена") ? .green : .orange)
                    }
                }
                Section {
                    Button {
                        Task { await translateAndAdd() }
                    } label: {
                        if isTranslating {
                            ProgressView()
                                .frame(maxWidth: .infinity, minHeight: 44)
                        } else {
                            Text("Перевести и в тренажёр")
                                .font(.headline)
                                .frame(maxWidth: .infinity, minHeight: 44)
                        }
                    }
                    .disabled(isTranslating || ownRU.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                } footer: {
                    Text("Перевод через Gemini (ключ из Настроек / Keychain). EN попадёт в тренажёр для проговаривания.")
                }
            }
            .navigationTitle("Своя фраза")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Закрыть") { showAddOwn = false }
                }
            }
        }
        .presentationDetents([.medium, .large])
    }

    private func reload() {
        items = PhrasalTrainerStore.load()
    }

    private func translateAndAdd() async {
        let ru = ownRU.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !ru.isEmpty else { return }
        guard settings.geminiEnabledAndReady else {
            addNote = settings.useGemini
                ? "Нет ключа Gemini в Настройках"
                : "Включи Gemini в Настройках"
            return
        }
        isTranslating = true
        addNote = "Перевожу…"
        defer { isTranslating = false }
        do {
            let result = try await GeminiSiteCoachService.shared.translateThrowing(
                text: ru,
                sourceHint: .ru
            )
            let en = result.translatedText.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !en.isEmpty, en != "(перевод позже)" else {
                addNote = "Пустой перевод — попробуй другую фразу"
                return
            }
            let phrase = PhrasalTrainerPhrase(
                en: en,
                ru: result.sourceText.isEmpty ? ru : result.sourceText,
                phrasal: "",
                source: "user_gemini"
            )
            let added = PhrasalTrainerStore.add(phrase)
            reload()
            addNote = added ? "EN добавлена в тренажёр: \(en)" : "Уже была в тренажёре: \(en)"
            toast = addNote
            ownRU = ""
        } catch let e as GeminiRequestError {
            addNote = e.shortRU
        } catch {
            addNote = "Нет сети / таймаут Gemini"
        }
    }
}

/// Sequential drill for trainer deck (reuse speak controls per card).
struct PhrasalTrainerDrillView: View {
    let phrases: [PhrasalTrainerPhrase]
    let startIndex: Int

    @State private var index: Int = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("\(min(index + 1, phrases.count)) / \(phrases.count)")
                .font(.headline)
            if phrases.indices.contains(index) {
                let p = phrases[index]
                Text(p.en)
                    .font(.title2.weight(.bold))
                if !p.ru.isEmpty {
                    Text(p.ru)
                        .font(.title3)
                        .foregroundStyle(.secondary)
                }
                PhrasalSpeakPracticeControls(en: p.en, ru: p.ru)
                HStack {
                    Button("Назад") { index = max(0, index - 1) }
                        .disabled(index == 0)
                    Spacer()
                    Button(index + 1 >= phrases.count ? "Готово" : "Дальше") {
                        if index + 1 >= phrases.count {
                            // stay on last
                        } else {
                            index += 1
                        }
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
            Spacer()
        }
        .padding(16)
        .navigationTitle("Гонять")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { index = min(max(0, startIndex), max(phrases.count - 1, 0)) }
    }
}
