import Foundation

/// Drop-in session engine for English On Site Репетитор.
/// Wire to Gemini (JSON in / JSON out) + ElevenLabs/AVSpeech on Kolya.
/// Pedagogy: docs/english-onsite-v4/LEARNING-CORE.md + TUTOR-DIALOGUE-PROTOCOL.md
/// Immersion lite: docs/english-onsite-v4/IMMERSION-STACK.md

enum TutorPhase: String, Codable {
    case idle, open, warm_retrieval, task_run, repair, focus_flash, close, persist
}

enum TutorExpect: String, Codable {
    case free, reproduction, self_eval, yes_no
}

struct MissItem: Codable, Identifiable, Equatable {
    var id: String { item + "|" + (context ?? "") }
    var item: String
    var context: String?
    var due: Date
    var ease: Double
    var intervalDays: Int
    /// Site frequency tag 1…5 (from scenario lexis).
    var frequency: Int
    var failCount: Int
    var successCount: Int
    var lastReviewedAt: Date?

    init(
        item: String,
        context: String? = nil,
        due: Date,
        ease: Double = 2.3,
        intervalDays: Int = 1,
        frequency: Int = 3,
        failCount: Int = 0,
        successCount: Int = 0,
        lastReviewedAt: Date? = nil
    ) {
        self.item = item
        self.context = context
        self.due = due
        self.ease = ease
        self.intervalDays = intervalDays
        self.frequency = frequency
        self.failCount = failCount
        self.successCount = successCount
        self.lastReviewedAt = lastReviewedAt
    }
}

struct LearnerModel: Codable {
    var cefr: String
    var l1: String
    var goalTags: [String]
    var focusForms: [String]
    var missBank: [MissItem]
    var lastCanDo: String?
    var lastWin: String?
    var lastNext: String?
    var ilrLite: String
}

struct TutorSessionConfig: Codable {
    var canDo: String
    var taskBrief: String
    var focusForm: String?
    var minutes: Int
    var scenarioId: String?
    var tutorRole: String?
    var sayItTargets: [String]
    var lexisFrequency: [String: Int]

    init(
        canDo: String,
        taskBrief: String,
        focusForm: String? = nil,
        minutes: Int = 10,
        scenarioId: String? = nil,
        tutorRole: String? = nil,
        sayItTargets: [String] = [],
        lexisFrequency: [String: Int] = [:]
    ) {
        self.canDo = canDo
        self.taskBrief = taskBrief
        self.focusForm = focusForm
        self.minutes = minutes
        self.scenarioId = scenarioId
        self.tutorRole = tutorRole
        self.sayItTargets = sayItTargets
        self.lexisFrequency = lexisFrequency
    }

    static func fromIrishScenario(_ scenario: [String: Any]) -> TutorSessionConfig? {
        guard
            let canDo = scenario["can_do"] as? String,
            let brief = scenario["task_brief"] as? String
        else { return nil }

        var freq: [String: Int] = [:]
        if let lexis = scenario["lexis"] as? [[String: Any]] {
            for row in lexis {
                if let en = row["en"] as? String {
                    freq[en.lowercased()] = (row["frequency"] as? Int) ?? 3
                }
            }
        }

        return TutorSessionConfig(
            canDo: canDo,
            taskBrief: brief,
            focusForm: scenario["focus_form"] as? String,
            minutes: 10,
            scenarioId: scenario["id"] as? String,
            tutorRole: scenario["tutor_role"] as? String,
            sayItTargets: scenario["say_it"] as? [String] ?? [],
            lexisFrequency: freq
        )
    }
}

struct TutorTurnRequest: Codable {
    var protocolVersion: Int = 1
    var phase: TutorPhase
    var learner: LearnerSnapshot
    var session: SessionSnapshot
    var learnerUtterance: String

    struct LearnerSnapshot: Codable {
        var cefr: String
        var l1: String
        var ilrLite: String
        var goalTags: [String]
        var focusForms: [String]
        var missBankDue: [[String: String]]
    }

    struct SessionSnapshot: Codable {
        var canDo: String
        var minutesLeft: Int
        var repairLevel: Int
        var focusForm: String?
        var lastTutorMove: String
        var taskBrief: String
        var scenarioId: String?
        var tutorRole: String?
        var sayItHint: String?
    }
}

struct TutorTurnResponse: Codable {
    var phase: TutorPhase
    var repairLevel: Int
    var speak: String
    var speakLocale: String
    var expectLearner: TutorExpect
    var targetForm: String?
    var recast: String?
    var logMiss: Bool
    var missItem: String?
    var ui: UIHints?
    var sessionPatch: SessionPatch?
    var endSession: Bool

    struct UIHints: Codable {
        var coachChip: String?
        var showRuGloss: Bool?
        var sayItHighlight: String?
    }

    struct SessionPatch: Codable {
        var canDoProgress: Double?
    }

    enum CodingKeys: String, CodingKey {
        case phase
        case repairLevel = "repair_level"
        case speak
        case speakLocale = "speak_locale"
        case expectLearner = "expect_learner"
        case targetForm = "target_form"
        case recast
        case logMiss = "log_miss"
        case missItem = "miss_item"
        case ui
        case sessionPatch = "session_patch"
        case endSession = "end_session"
    }
}

/// Soft match for tutor reproduction turns (looser than Roleplay Loop 0.75).
enum TutorReproductionGate {
    static let passThreshold: Double = 0.70

    static func passes(transcript: String, target: String, scorer: (String, String) -> Double) -> Bool {
        scorer(transcript, target) >= passThreshold
    }
}

final class TutorSessionEngine {
    private(set) var phase: TutorPhase = .idle
    private(set) var repairLevel: Int = 0
    private(set) var canDoProgress: Double = 0
    private(set) var learner: LearnerModel
    private let config: TutorSessionConfig
    private var startedAt = Date()
    private var lastTutorMove = "open"
    private var sayItIndex = 0

    init(learner: LearnerModel, config: TutorSessionConfig) {
        self.learner = learner
        self.config = config
    }

    var minutesLeft: Int {
        max(0, config.minutes - Int(Date().timeIntervalSince(startedAt) / 60))
    }

    func start() -> TutorTurnRequest {
        phase = .open
        repairLevel = 0
        canDoProgress = 0
        sayItIndex = 0
        startedAt = Date()
        return makeRequest(utterance: "")
    }

    func makeRequest(utterance: String) -> TutorTurnRequest {
        let warm = PredictiveReviewEngine.nextWarmItems(from: learner.missBank)
            .map {
                [
                    "item": $0.item,
                    "hint_context": $0.context ?? config.canDo,
                    "priority": String(format: "%.2f", $0.priority),
                    "frequency": String($0.frequency)
                ]
            }

        let sayHint: String? = {
            guard !config.sayItTargets.isEmpty else { return nil }
            return config.sayItTargets[sayItIndex % config.sayItTargets.count]
        }()

        return TutorTurnRequest(
            phase: phase == .idle ? .open : phase,
            learner: .init(
                cefr: learner.cefr,
                l1: learner.l1,
                ilrLite: learner.ilrLite,
                goalTags: learner.goalTags,
                focusForms: learner.focusForms,
                missBankDue: warm
            ),
            session: .init(
                canDo: config.canDo,
                minutesLeft: minutesLeft,
                repairLevel: repairLevel,
                focusForm: config.focusForm,
                lastTutorMove: lastTutorMove,
                taskBrief: config.taskBrief,
                scenarioId: config.scenarioId,
                tutorRole: config.tutorRole,
                sayItHint: sayHint
            ),
            learnerUtterance: utterance
        )
    }

    @discardableResult
    func apply(_ response: TutorTurnResponse) -> TutorTurnResponse {
        phase = response.phase
        repairLevel = max(0, min(5, response.repairLevel))
        if let p = response.sessionPatch?.canDoProgress {
            canDoProgress = min(1, max(0, p))
        }
        lastTutorMove = response.expectLearner.rawValue

        if response.logMiss, let item = response.missItem, !item.isEmpty {
            let freq = frequencyFor(phrase: item)
            PredictiveReviewEngine.upsertFail(
                bank: &learner.missBank,
                phrase: item,
                context: config.scenarioId ?? config.taskBrief,
                frequency: freq
            )
        }

        if response.phase == .focus_flash || response.ui?.sayItHighlight != nil {
            sayItIndex += 1
        }

        if response.endSession {
            phase = .persist
            learner.lastCanDo = config.canDo
        }
        return response
    }

    func bumpRepairAfterFailedReproduction() {
        repairLevel = min(5, repairLevel + 1)
        phase = .repair
    }

    func markReproductionSuccess(_ phrase: String) {
        markSuccessIfKnown(phrase)
        repairLevel = 0
        if phase == .repair { phase = .task_run }
    }

    private func markSuccessIfKnown(_ phrase: String) {
        if let idx = learner.missBank.firstIndex(where: {
            $0.item.compare(phrase, options: [.caseInsensitive, .diacriticInsensitive]) == .orderedSame
        }) {
            PredictiveReviewEngine.scheduleSuccess(&learner.missBank[idx])
        }
    }

    private func frequencyFor(phrase: String) -> Int {
        let lower = phrase.lowercased()
        for (key, value) in config.lexisFrequency where lower.contains(key) {
            return value
        }
        return 3
    }
}

enum TutorJSON {
    static let responseDecoder = JSONDecoder()

    static let requestEncoder: JSONEncoder = {
        let e = JSONEncoder()
        e.keyEncodingStrategy = .convertToSnakeCase
        e.outputFormatting = [.sortedKeys]
        return e
    }()

    static func decodeResponse(_ data: Data) throws -> TutorTurnResponse {
        try responseDecoder.decode(TutorTurnResponse.self, from: data)
    }

    static func encodeRequest(_ request: TutorTurnRequest) throws -> Data {
        try requestEncoder.encode(request)
    }
}

enum IrishSitePackLoader {
    static func loadScenarios(from data: Data) throws -> [[String: Any]] {
        let root = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        return root?["scenarios"] as? [[String: Any]] ?? []
    }

    static func config(scenarioId: String, data: Data) throws -> TutorSessionConfig? {
        try loadScenarios(from: data)
            .first { ($0["id"] as? String) == scenarioId }
            .flatMap(TutorSessionConfig.fromIrishScenario)
    }
}
