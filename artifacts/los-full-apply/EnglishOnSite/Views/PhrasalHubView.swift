import SwiftUI

/// Root tab «Фразовые» — Duolingo match game first (EN left · RU right).
struct PhrasalHubView: View {
    @State private var contentMode: TutorContentMode = .site
    @State private var gameKind: GameKind = .phrasal

    private enum GameKind: String, CaseIterable, Identifiable {
        case phrasal
        case words
        var id: String { rawValue }
        var title: String {
            switch self {
            case .phrasal: return "Фразовые"
            case .words: return "Слова"
            }
        }
        var pairsMode: TutorPairsMode {
            switch self {
            case .phrasal: return .phrasal
            case .words: return .words
            }
        }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("Банк", selection: $contentMode) {
                    ForEach(TutorContentMode.allCases) { mode in
                        Text(mode.titleRU).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 16)
                .padding(.top, 12)
                .onChange(of: contentMode) { _, mode in
                    TutorBankStore.setMode(mode)
                }

                Picker("Игра", selection: $gameKind) {
                    ForEach(GameKind.allCases) { kind in
                        Text(kind.title).tag(kind)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 16)
                .padding(.top, 8)

                HStack(spacing: 10) {
                    NavigationLink {
                        TutorPhrasalSearchView()
                    } label: {
                        Label("Поиск", systemImage: "magnifyingglass")
                            .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.bordered)

                    NavigationLink {
                        PhrasalToolsView()
                    } label: {
                        Label("Инструменты", systemImage: "wrench.and.screwdriver")
                            .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.bordered)

                    NavigationLink {
                        PhrasalTrainerView()
                    } label: {
                        Label("Тренажёр", systemImage: "mic.badge.plus")
                            .font(.caption.weight(.semibold))
                    }
                    .buttonStyle(.bordered)

                    Spacer(minLength: 0)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
                .padding(.bottom, 4)

                // Primary: Duolingo-style match (not a vertical list of five).
                TutorPairsView(mode: gameKind.pairsMode)
                    .id("\(contentMode.rawValue)-\(gameKind.rawValue)")
            }
            .navigationTitle("Фразовые")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear { TutorBankStore.setMode(contentMode) }
        }
    }
}
