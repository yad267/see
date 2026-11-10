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
            Section {
                Picker("Режим", selection: Bindable(settings).learningMode) {
                    ForEach(AppLearningMode.allCases) { m in
                        Text(m.title).tag(m)
                    }
                }
                .pickerStyle(.segmented)

                Text(mode.blurbRU)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .listRowBackground(Color.clear)

                if mode == .onSite {
                    Text(LessonStore.shared.lastStatusRU)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                        .listRowBackground(Color.clear)
                }
            }

            if mode == .onSite {
                onSiteActions
            } else {
                regularActions
            }

            if let next = visibleLessons.first(where: { !LessonProgressStore.isCompleted($0.id) }) {
                Section("Продолжить") {
                    lessonLink(next)
                }
            }

            Section(mode == .onSite ? "Path · On site" : "Диалоги · Regular") {
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
        .listStyle(.insetGrouped)
        .navigationTitle(mode == .onSite ? "Language on Site" : "Regular Language")
        .navigationBarTitleDisplayMode(.large)
        .onAppear { repository.reload() }
    }

    @ViewBuilder
    private var onSiteActions: some View {
        Section {
            Button {
                showCreateLesson = true
            } label: {
                Label("Новый урок · объект", systemImage: "plus.circle.fill")
                    .font(.title3.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 10)
            }
            .buttonStyle(.borderedProminent)
            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
            .listRowBackground(Color.clear)
        }

        Section {
            NavigationLink {
                OnSiteMenuView()
            } label: {
                Label("On site", systemImage: "helmet.safety")
                    .font(.headline)
                    .padding(.vertical, 8)
            }

            NavigationLink {
                TranslateView()
            } label: {
                Label("Перевод", systemImage: "character.book.closed")
                    .font(.headline)
                    .padding(.vertical, 8)
            }
        }
    }

    @ViewBuilder
    private var regularActions: some View {
        Section {
            NavigationLink {
                RegularLanguageMenuView()
            } label: {
                Label("Regular Language", systemImage: "text.book.closed.fill")
                    .font(.title3.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 10)
            }
            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))

            Text("Фразовые · Лёгкие фразы · Диалоги — каждый раздел с уровнями A1–C2.")
                .font(.caption)
                .foregroundStyle(.secondary)
        }

        Section {
            NavigationLink {
                TranslateView()
            } label: {
                Label("Перевод", systemImage: "character.book.closed")
                    .font(.headline)
                    .padding(.vertical, 8)
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

                HStack(spacing: 8) {
                    ForEach(lesson.tags.filter { $0 != "induction" && $0 != "general" }, id: \.self) { tag in
                        Text(tag)
                            .font(.caption.weight(.medium))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(Color.accentColor.opacity(0.15))
                            .clipShape(Capsule())
                    }
                }
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
