import SwiftUI

/// B14: root tab «Фразовые» — Duolingo-style search/pairs first; tools & trainer secondary.
struct PhrasalHubView: View {
    @State private var contentMode: TutorContentMode = .site

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("Режим", selection: $contentMode) {
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

                // Secondary: keep tools/trainer reachable without replacing Duolingo pairs UX.
                HStack(spacing: 10) {
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

                // Primary: tap words / Погнал · Пары (Duolingo-style)
                TutorPhrasalSearchView()
            }
            .navigationTitle("Фразовые")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear { TutorBankStore.setMode(contentMode) }
        }
    }
}
