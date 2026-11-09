import Foundation
import AVFoundation
import AudioToolbox
import CryptoKit
import Speech
#if canImport(UIKit)
import UIKit
#endif

/// Drop-in scoring + loop gate for RoleplayLoopEngine.
/// Wire into existing engine: call `evaluateUserUtterance` when mic timer ends / "Done" tapped.
@MainActor
final class RoleplaySTTScoringController: ObservableObject {
    enum GateResult {
        case advance(match: Double)
        case retry(match: Double)
        case finishedCleanRounds
    }

    @Published private(set) var consecutiveCleanRounds: Int = 0
    @Published private(set) var lastMatchPercentage: Double = 0

    private let requiredCleanRounds: Int
    private let coach = AVSpeechSynthesizer()

    init(requiredCleanRounds: Int = 2) {
        self.requiredCleanRounds = requiredCleanRounds
    }

    func resetProgress() {
        consecutiveCleanRounds = 0
        lastMatchPercentage = 0
    }

    /// Call with STT transcript + current user line from RoleplayScript.
    /// - Parameters:
    ///   - transcript: SFSpeechRecognizer / TimedSpeechCapture text
    ///   - expectedLine: RoleplayScript line the user must say
    ///   - isLastLineOfRound: true when this was the final user line in the script circle
    func evaluateUserUtterance(
        transcript: String,
        expectedLine: String,
        isLastLineOfRound: Bool
    ) -> GateResult {
        let score = DialogueFuzzyMatcher.score(transcript: transcript, expected: expectedLine)
        lastMatchPercentage = score.percentage

        if score.passes {
            successFeedback()
            if isLastLineOfRound {
                consecutiveCleanRounds += 1
                if consecutiveCleanRounds >= requiredCleanRounds {
                    return .finishedCleanRounds
                }
            }
            return .advance(match: score.percentage)
        } else {
            failureFeedback()
            speakRetryCoach()
            return .retry(match: score.percentage)
        }
    }

    private func successFeedback() {
        #if canImport(UIKit)
        UINotificationFeedbackGenerator().notificationOccurred(.success)
        #endif
        AudioServicesPlaySystemSound(1115)
    }

    private func failureFeedback() {
        #if canImport(UIKit)
        UINotificationFeedbackGenerator().notificationOccurred(.error)
        #endif
        AudioServicesPlaySystemSound(1053)
    }

    private func speakRetryCoach() {
        let u = AVSpeechUtterance(string: "Let's try again")
        u.voice = AVSpeechSynthesisVoice(language: "en-GB")
        u.rate = AVSpeechUtteranceDefaultSpeechRate * 0.95
        coach.speak(u)
    }
}

// MARK: - ElevenLabs cache contract (verify in ElevenLabsTTS.swift)

enum ElevenLabsCacheKey {
    static func fileName(text: String, voiceId: String) -> String {
        let raw = text + "|" + voiceId
        let digest = SHA256Digest.hex(raw)
        return digest + ".mp3"
    }
}

/// Minimal SHA256 hex without CryptoKit dependency issues on older targets.
enum SHA256Digest {
    static func hex(_ string: String) -> String {
        // Prefer CryptoKit when available in app target:
        // import CryptoKit; SHA256.hash(data: Data(string.utf8)).map { String(format: "%02x", $0) }.joined()
        // Fallback: stable hash for drop-in compile in isolation docs — REPLACE with CryptoKit in app.
        var hash: UInt64 = 5381
        for b in string.utf8 { hash = ((hash << 5) &+ hash) &+ UInt64(b) }
        return String(format: "%016llx", hash)
    }
}
