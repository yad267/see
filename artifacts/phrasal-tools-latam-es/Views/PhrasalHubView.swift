import SwiftUI

/// B14: root tab «Фразовые» — tools pack / trainer + site|general search.
struct PhrasalHubView: View {
    @State private var contentMode: TutorContentMode = .site

    var body: some View {
        NavigationStack {
            List {
                Section("Инструменты · тренажёр") {
                    NavigationLink {
                        PhrasalToolsView()
                    } label: {
                        Label("Фразы с инструментами", systemImage: "wrench.and.screwdriver")
                    }
                    NavigationLink {
                        PhrasalTrainerView()
                    } label: {
                        Label("Тренажёр", systemImage: "mic.badge.plus")
                    }
                }

                Section("Поиск · банк") {
                    Picker("Режим", selection: $contentMode) {
                        ForEach(TutorContentMode.allCases) { mode in
                            Text(mode.titleRU).tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)
                    .onChange(of: contentMode) { _, mode in
                        TutorBankStore.setMode(mode)
                    }

                    NavigationLink {
                        TutorPhrasalSearchView()
                    } label: {
                        Label("Искать фразовый", systemImage: "magnifyingglass")
                    }
                }
            }
            .navigationTitle("Фразовые")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear { TutorBankStore.setMode(contentMode) }
        }
    }
}
