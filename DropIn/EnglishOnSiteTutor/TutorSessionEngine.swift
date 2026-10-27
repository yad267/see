import Foundation

/// Drop-in session engine for English On Site Репетитор.
/// Wire to Gemini (JSON in / JSON out) + ElevenLabs/AVSpeech on Kolya.
/// Pedagogy: docs/english-onsite-v4/LEARNING-CORE.md + TUTOR-DIALOGUE-PROTOCOL.md

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
}

struct TutorSessionConfig: Codable {
    var canDo: String
    var taskBrief: String
    var focusForm: String?
    var minutes: Int
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

    /// SM-2-ish defaults: 1 → 3 → 7 → 21 days.
    private let defaultIntervals = [1, 3, 7, 21]

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
        startedAt = Date()
        return makeRequest(utterance: "")
    }

    func makeRequest(utterance: String) -> TutorTurnRequest {
        let due = learner.missBank
            .filter { $0.due <= Date() }
            .prefix(2)
            .map { ["item": $0.item, "hint_context": $0.context ?? config.canDo] }

        return TutorTurnRequest(
            phase: phase == .idle ? .open : phase,
            learner: .init(
                cefr: learner.cefr,
                l1: learner.l1,
                goalTags: learner.goalTags,
                focusForms: learner.focusForms,
                missBankDue: Array(due)
            ),
            session: .init(
                canDo: config.canDo,
                minutesLeft: minutesLeft,
                repairLevel: repairLevel,
                focusForm: config.focusForm,
                lastTutorMove: lastTutorMove,
                taskBrief: config.taskBrief
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
            scheduleMiss(item, context: config.taskBrief)
        }

        if response.endSession {
            phase = .persist
            learner.lastCanDo = config.canDo
        }
        return response
    }

    /// After local soft-fail on reproduction, bump ladder without calling the model yet (optional).
    func bumpRepairAfterFailedReproduction() {
        repairLevel = min(5, repairLevel + 1)
        phase = .repair
    }

    private func scheduleMiss(_ item: String, context: String) {
        if let idx = learner.missBank.firstIndex(where: { $0.item == item }) {
            var m = learner.missBank[idx]
            let step = min(m.intervalDays, defaultIntervals.count - 1)
            let next = defaultIntervals[min(step + 1, defaultIntervals.count - 1)]
            m.intervalDays = next
            m.due = Calendar.current.date(byAdding: .day, value: next, to: Date()) ?? Date()
            m.ease = min(3.0, m.ease + 0.1)
            learner.missBank[idx] = m
        } else {
            learner.missBank.append(
                MissItem(
                    item: item,
                    context: context,
                    due: Calendar.current.date(byAdding: .day, value: defaultIntervals[0], to: Date()) ?? Date(),
                    ease: 2.3,
                    intervalDays: defaultIntervals[0]
                )
            )
        }
    }
}

enum TutorJSON {
    /// Response uses explicit `CodingKeys` (snake_case). Do not also convertFromSnakeCase.
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
