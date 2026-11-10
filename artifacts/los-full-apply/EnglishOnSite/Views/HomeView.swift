import SwiftUI

struct HomeView: View {
    @Environment(AppSettings.self) private var settings
    @Bindable var repository: LessonRepository
    @Binding var path: NavigationPath
    @Binding var showCreateLesson: Bool

    private var mode: AppLearningMode {
        settings.learningMode
    }

    private var visibleLessons: [Lesson] {
        switch mode {
        case .onSite:
            return repository.lessons.filter { !$0.tags.contains("general") }
        case .regular:
            return repository.lessons.filter {
                $0.tags.contains("general") || $0.createdBy == "user_gemini_general"
            }
        }
    }

    var body: some View {
        List {
            // Top choice: Regular Language | On site
            Section {
                Picker("Режим", selection: Bindable(settings).learningMode) {
                    ForEach(AppLearningMode.allCases) { m in
                        Text(m.pickerLabel).tag(m)
                    }
                }
                .pickerStyle(.segmented)
                .accessibilityLabel("Выбор режима: Regular Language или On site")

                Text(mode.blurbRU)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } header: {
                Text("Выбери режим")
            }

            // Mode content appears immediately under the picker
            if mode == .onSite {
                onSiteModeContent
            } else {
                regularModeContent
            }

            if let next = visibleLessons.first(where: { !LessonProgressStore.isCompleted($0.id) }) {
                Section("Продолжить") {
                    lessonLink(next)
                }
            }

            Section(mode == .onSite ? "Path · On site" : "Мои диалоги · Regular") {
                if visibleLessons.isEmpty {
                    Text(mode == .onSite
                         ? "Пока нет уроков Path / своих site-уроков."
                         : "Пока нет собранных диалогов — открой Диалоги → уровень → тема.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(visibleLessons) { lesson in
                        lessonLink(lesson)
                            .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                                if lesson.isUserLesson {
                                    Button(role: .destructive) {
                                        try? repository.deleteUser(id: lesson.id)
                                    } label: {
                                        Label("Удалить", systemImage: "trash")
                                    }
                                }
                            }
                    }
                }
            }

            Section {
                NavigationLink {
                    TranslateView()
                } label: {
                    Label("Перевод", systemImage: "character.book.closed")
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle(mode.title)
        .navigationBarTitleDisplayMode(.large)
        .onAppear { repository.reload() }
        .onChange(of: settings.learningMode) { _, newMode in
            if newMode == .regular {
                TutorBankStore.setMode(.general)
            } else {
                TutorBankStore.setMode(.site)
            }
        }
    }

    /// On site (Language on Site): CEFR levels A1–C2 right on Уроки.
    @ViewBuilder
    private var onSiteModeContent: some View {
        Section {
            Button {
                showCreateLesson = true
            } label: {
                Label("Новый урок · объект", systemImage: "plus.circle.fill")
                    .font(.headline)
            }
        }

        Section("On site · уровень CEFR") {
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

    /// Regular Language: three sections on Уроки (each opens CEFR A1–C2).
    @ViewBuilder
    private var regularModeContent: some View {
        Section("Regular Language · разделы") {
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

    private func lessonLink(_ lesson: Lesson) -> some View {
        NavigationLink(value: lesson) {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline) {
                    Text(lesson.titleRu)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(.primary)
                        .multilineTextAlignment(.leading)
                    if LessonProgressStore.isCompleted(lesson.id) {
                        Text("✓")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(.green)
                    }
                    if lesson.isSiteInduction {
                        chip("Site induction")
                    } else if lesson.tags.contains("containment") {
                        chip("Containment")
                    } else if lesson.tags.contains("general") {
                        chip("General")
                    }
                    if lesson.isUserLesson {
                        Text("Мой")
                            .font(.caption2.weight(.bold))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Color.orange.opacity(0.2))
                            .foregroundStyle(.orange)
                            .clipShape(Capsule())
                    }
                }

                if let titleEn = lesson.titleEn, !titleEn.isEmpty {
                    Text(titleEn)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.secondary)
                }

                Text(lesson.sceneRu)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }
            .padding(.vertical, 8)
        }
    }

    private func chip(_ text: String) -> some View {
        Text(text)
            .font(.caption2.weight(.bold))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(Color.accentColor.opacity(0.18))
            .foregroundStyle(.tint)
            .clipShape(Capsule())
    }
}
