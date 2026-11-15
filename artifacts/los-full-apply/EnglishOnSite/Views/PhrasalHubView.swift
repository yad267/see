import SwiftUI

/// Tab «Фразовые»: Onsite | Regular → Duolingo pairs; family (get/take…) or mixed.
struct PhrasalHubView: View {
    @State private var track: PhrasalTrack = .onsite
    @State private var roundKind: PhrasalRoundKind = .mixed
    @State private var seedPhrasals: [PhrasalEntry] = []

    private enum PhrasalTrack: String, CaseIterable, Identifiable {
        case onsite, regular
        var id: String { rawValue }
        var title: String {
            switch self {
            case .onsite: return "Onsite"
            case .regular: return "Regular"
            }
        }
        var bankMode: TutorContentMode {
            switch self {
            case .onsite: return .site
            case .regular: return .general
            }
        }
    }

    private enum PhrasalRoundKind: String, CaseIterable, Identifiable {
        case mixed, get, take, put, turn, look, come
        var id: String { rawValue }
        var title: String {
            switch self {
            case .mixed: return "Смешанный"
            case .get: return "get"
            case .take: return "take"
            case .put: return "put"
            case .turn: return "turn"
            case .look: return "look"
            case .come: return "come"
            }
        }
        var rootFilter: String? {
            switch self {
            case .mixed: return nil
            default: return rawValue
            }
        }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("Режим", selection: $track) {
                    ForEach(PhrasalTrack.allCases) { t in
                        Text(t.title).tag(t)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 16)
                .padding(.top, 12)
                .onChange(of: track) { _, t in
                    TutorBankStore.setMode(t.bankMode)
                    reloadSeed()
                }

                Text(track == .onsite
                     ? "Onsite phrasal · Duolingo: слева EN, справа RU"
                     : "Regular phrasal · та же игра, бытовой банк")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)
                    .padding(.top, 8)

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(PhrasalRoundKind.allCases) { kind in
                            Button {
                                roundKind = kind
                                reloadSeed()
                            } label: {
                                Text(kind.title)
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 8)
                                    .background(
                                        roundKind == kind
                                        ? Color.accentColor.opacity(0.2)
                                        : Color.secondary.opacity(0.12),
                                        in: Capsule()
                                    )
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                }

                TutorPairsView(mode: .phrasal, seedPhrasals: seedPhrasals)
                    .id(seedPhrasals.map(\.en).joined(separator: "|"))
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            // Keep all hub content above the tab bar; TutorPairsView scrolls internally.
            .safeAreaPadding(.bottom, 4)
            .navigationTitle("Фразовые")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                TutorBankStore.setMode(track.bankMode)
                if seedPhrasals.isEmpty { reloadSeed() }
            }
        }
    }

    private func reloadSeed() {
        TutorBankStore.ensureLoaded()
        let all = TutorBankStore.phrasals
        // Mixed: small Duolingo round. Family (get/come/…): show high‑freq set for that root (cap 8).
        guard let root = roundKind.rootFilter else {
            seedPhrasals = Array(all.shuffled().prefix(5))
            return
        }
        let filtered = all.filter {
            $0.root.lowercased() == root
                || $0.en.lowercased().split(separator: " ").first.map(String.init) == root
        }
        if filtered.count >= 3 {
            seedPhrasals = Array(filtered.shuffled().prefix(8))
            return
        }
        let loose = all.filter { $0.en.lowercased().contains(root) }
        seedPhrasals = Array((loose.isEmpty ? all : loose).shuffled().prefix(8))
    }
}
