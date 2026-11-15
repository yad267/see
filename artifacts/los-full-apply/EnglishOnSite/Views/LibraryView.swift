import SwiftUI
import SwiftData
import AVFoundation

/// «Мои фразы»: одна база + «Знаю»/«Забыл» + повтор. TTS on Знаю and Забыл.
struct LibraryView: View {
    @Environment(AppSettings.self) private var settings
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \LibraryItem.createdAt, order: .reverse) private var items: [LibraryItem]

    @State private var filter: LibraryFilter = .all
    @State private var speaker: SpeechSpeaker?
    @State private var localPlayer: AVAudioPlayer?
    @State private var showReview = false
    @State private var showAdd = false
    @State private var phrasalSeedNote: String?

    enum LibraryFilter: String, CaseIterable, Identifiable {
        case all, learning, known, due
        var id: String { rawValue }
        var title: String {
            switch self {
            case .all: return "Все"
            case .learning: return "Учу"
            case .known: return "Изученные"
            case .due: return "Повтор"
            }
        }
    }

    private var filtered: [LibraryItem] {
        switch filter {
        case .all: return items
        case .learning: return items.filter(\.isLearningNew)
        case .known: return items.filter(\.known)
        case .due: return items.filter { $0.known && $0.isDue }
        }
    }

    private var dueForReview: [LibraryItem] {
        LibraryStore.dueItems(items, limit: 8)
    }

    var body: some View {
        List {
            Section {
                Picker("Фильтр", selection: $filter) {
                    ForEach(LibraryFilter.allCases) { f in
                        Text(f.title).tag(f)
                    }
                }
                .pickerStyle(.segmented)

                Button {
                    showAdd = true
                } label: {
                    Label("Добавить фразу", systemImage: "plus.circle.fill")
                        .font(.headline)
                        .frame(maxWidth: .infinity, minHeight: 44)
                }

                Button {
                    let added = LearningBankStore.seedPhrasalsIntoLibrary(context: modelContext)
                    phrasalSeedNote = added == 0
                        ? "Фразовые уже были в базе."
                        : "Закинул фразовых: \(added)."
                } label: {
                    Label("Добавить фразовые глаголы", systemImage: "text.badge.plus")
                        .font(.headline)
                        .frame(maxWidth: .infinity, minHeight: 44)
                }

                if let phrasalSeedNote {
                    Text(phrasalSeedNote)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Button {
                    showReview = true
                } label: {
                    Label("Повтор (\(dueForReview.count))", systemImage: "rectangle.stack")
                        .font(.headline)
                        .frame(maxWidth: .infinity, minHeight: 44)
                }
                .disabled(dueForReview.isEmpty)
            }

            if filtered.isEmpty {
                Section {
                    Text("Добавь фразу или отметь «Знаю» в банке.")
                        .foregroundStyle(.secondary)
                        .padding(.vertical, 8)
                }
            } else {
                Section("Фразы · \(filtered.count)") {
                    ForEach(filtered, id: \.id) { item in
                        card(item)
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Мои фразы")
        .onAppear {
            if speaker == nil { speaker = SpeechSpeaker(settings: settings) }
        }
        .onDisappear {
            speaker?.stop()
            localPlayer?.stop()
        }
        .navigationDestination(isPresented: $showReview) {
            ReviewSessionView(items: dueForReview)
        }
        .sheet(isPresented: $showAdd) {
            AddMyPhraseView(source: .manual)
                .presentationDragIndicator(.visible)
        }
    }

    private func card(_ item: LibraryItem) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(item.en)
                    .font(.title3.weight(.bold))
                Spacer()
                if item.known {
                    Text("Знаю")
                        .font(.caption2.weight(.bold))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green.opacity(0.2))
                        .clipShape(Capsule())
                }
            }
            Text(item.ru)
                .font(.body)
                .foregroundStyle(.secondary)

            HStack(spacing: 8) {
                Button("▶") { playEN(item) }
                    .buttonStyle(.borderedProminent)
                Button(item.known ? "Забыл" : "Знаю") {
                    // Speak on both paths (Забыл = «нет, не знаю»).
                    playEN(item)
                    if item.known {
                        LibraryStore.unmarkKnown(item, context: modelContext)
                    } else {
                        LibraryStore.markKnown(item, context: modelContext)
                        Task { await ensureAudio(item) }
                    }
                }
                .buttonStyle(.bordered)
                Button("Удалить", role: .destructive) {
                    LibraryStore.delete(item, context: modelContext)
                }
                .buttonStyle(.bordered)
            }
            .font(.subheadline.weight(.semibold))
        }
        .padding(.vertical, 6)
    }

    private func playEN(_ item: LibraryItem) {
        if speaker == nil { speaker = SpeechSpeaker(settings: settings) }
        if let name = item.audioFileName, LibraryAudioStore.hasFile(name) {
            let url = LibraryAudioStore.fileURL(fileName: name)
            do {
                localPlayer = try AVAudioPlayer(contentsOf: url)
                localPlayer?.prepareToPlay()
                localPlayer?.play()
                return
            } catch {
                // fall through to TTS
            }
        }
        speaker?.updateSettings(settings)
        speaker?.speakEN(item.en)
        Task { await ensureAudio(item) }
    }

    private func ensureAudio(_ item: LibraryItem) async {
        await ElevenLabsTTS.shared.prefetchToDisk(text: item.en, lang: .en, settings: settings)
        let params = settings.elVoiceParams(for: .en)
        let voice = SiteVoiceLang.en.voiceId
        let cache = ElevenLabsAudioCache.fileURL(text: item.en, voice: voice, params: params)
        let preferred = item.audioFileName ?? "\(item.id.uuidString).mp3"
        if let name = LibraryAudioStore.bindFromCacheURL(cache, preferredName: preferred) {
            item.audioFileName = name
            item.audioCacheKey = ElevenLabsAudioCache.cacheKey(text: item.en, voice: voice, params: params)
            try? modelContext.save()
        }
    }
}
