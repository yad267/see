import Foundation

/// AFRL / Linguist Next–inspired lite scheduler:
/// priority = decay urgency × site frequency × fail weight.
/// Not a full cognitive model — portable drop-in for English On Site miss_bank.

struct ReviewCandidate: Equatable {
    var item: String
    var context: String?
    var priority: Double
    var due: Date
    var frequency: Int
    var failCount: Int
}

struct PredictiveReviewConfig {
    /// Hours until an item is considered fully “cold” without success.
    var halfLifeHours: Double = 36
    /// Weight for Irish-site frequency tags (1…5).
    var frequencyWeight: Double = 0.35
    /// Weight for repeated fails.
    var failWeight: Double = 0.45
    /// Weight for pure time-overdue factor.
    var decayWeight: Double = 0.55
    var maxWarmItems: Int = 2
}

enum PredictiveReviewEngine {
    static func priority(
        item: MissItem,
        now: Date = Date(),
        config: PredictiveReviewConfig = .init()
    ) -> Double {
        let overdueHours = max(0, now.timeIntervalSince(item.due) / 3600)
        let decay = 1 - exp(-overdueHours / max(1, config.halfLifeHours))
        let freq = Double(min(5, max(1, item.frequency))) / 5.0
        let fails = min(1.0, Double(item.failCount) / 4.0)
        return config.decayWeight * decay
            + config.frequencyWeight * freq
            + config.failWeight * fails
            + (item.due <= now ? 0.15 : 0)
    }

    static func nextWarmItems(
        from bank: [MissItem],
        now: Date = Date(),
        config: PredictiveReviewConfig = .init()
    ) -> [ReviewCandidate] {
        bank
            .map {
                ReviewCandidate(
                    item: $0.item,
                    context: $0.context,
                    priority: priority(item: $0, now: now, config: config),
                    due: $0.due,
                    frequency: $0.frequency,
                    failCount: $0.failCount
                )
            }
            .filter { $0.due <= now || $0.priority >= 0.35 }
            .sorted { $0.priority > $1.priority }
            .prefix(config.maxWarmItems)
            .map { $0 }
    }

    /// After a successful reproduction in a new context — stretch interval.
    static func scheduleSuccess(_ item: inout MissItem, now: Date = Date()) {
        let ladder = [1, 3, 7, 21, 45]
        let idx = ladder.firstIndex(of: item.intervalDays) ?? 0
        let next = ladder[min(idx + 1, ladder.count - 1)]
        item.intervalDays = next
        item.due = Calendar.current.date(byAdding: .day, value: next, to: now) ?? now
        item.ease = min(3.2, item.ease + 0.15)
        item.successCount += 1
        item.lastReviewedAt = now
    }

    /// After fail / log_miss — pull forward, bump failCount.
    static func scheduleFail(
        _ item: inout MissItem,
        frequency: Int = 3,
        now: Date = Date()
    ) {
        item.failCount += 1
        item.frequency = max(item.frequency, frequency)
        item.ease = max(1.3, item.ease - 0.2)
        let days = item.failCount >= 3 ? 0 : 1
        item.intervalDays = max(1, days == 0 ? 1 : days)
        item.due = Calendar.current.date(byAdding: .day, value: days, to: now) ?? now
        item.lastReviewedAt = now
    }

    static func upsertFail(
        bank: inout [MissItem],
        phrase: String,
        context: String?,
        frequency: Int,
        now: Date = Date()
    ) {
        if let idx = bank.firstIndex(where: { $0.item == phrase }) {
            scheduleFail(&bank[idx], frequency: frequency, now: now)
            if let context { bank[idx].context = context }
        } else {
            var fresh = MissItem(
                item: phrase,
                context: context,
                due: now,
                ease: 2.0,
                intervalDays: 1,
                frequency: frequency,
                failCount: 1,
                successCount: 0,
                lastReviewedAt: now
            )
            scheduleFail(&fresh, frequency: frequency, now: now)
            bank.append(fresh)
        }
    }
}
