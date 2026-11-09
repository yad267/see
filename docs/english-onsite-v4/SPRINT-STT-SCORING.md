# English Onsite v4 — Sprint: STT Scoring (drop-in)

**Status:** Cloud agent prepared code; **must be merged & built on Mac «Kolya»** inside `EnglishOnSite` (this Linux Cloud workspace has no Xcode / no app sources).

## Protocol accepted
- Zero-Question on minor UI/tech details
- Autonomous build/fix only where `xcodebuild` + project exist
- Sprint lock: iOS only (no n8n / Next.js)

## Files to add / wire

| File | Action |
|------|--------|
| `DropIn/EnglishOnSiteScoring/DialogueFuzzyMatcher.swift` | Copy into app target (e.g. `EnglishOnSite/Services/` or `Roleplay/`) |
| `DropIn/EnglishOnSiteScoring/RoleplaySTTScoringController` in patch file | Merge into / call from `RoleplayLoopEngine.swift` |
| `.cursorrules` | Already at repo root — copy into `EnglishOnSite` root |

## Wire into RoleplayLoopEngine (pseudo)

```swift
// On mic Done / TimedSpeechCapture finish:
let result = scoring.evaluateUserUtterance(
    transcript: capture.transcript,
    expectedLine: currentUserLine.text,
    isLastLineOfRound: isLastUserLine
)
switch result {
case .advance:
    playOpponentNext() // existing
case .retry:
    stayOnCurrentUserLine() // do NOT advance
case .finishedCleanRounds:
    showSuccessScreen() // exit Loop Mode
}
```

## ElevenLabs cache check (in ElevenLabsTTS.swift)

Before any HTTP TTS:
1. `key = SHA256(text + "|" + voice_id)`
2. If `Caches/.../key.mp3` exists → play local
3. Else → request API → write file → play

UI phrases (`Let's try again`) → **AVSpeech only**.

## Fuzzy rule
- normalize: lowercase, strip punctuation
- strip articles/small prepositions
- pass if word-overlap F1 ≥ **0.75**
- soft Levenshtein on words length ≥ 4

## Owner command for Kolya Cursor (paste there)

```text
Open EnglishOnSite project. Apply STT scoring sprint from PRD:
- Fuzzy match 75% in RoleplayLoopEngine
- Block advance on fail; AVSpeech "Let's try again"
- consecutiveCleanRounds == 2 → exit success
- Verify ElevenLabs cache before API
Create/update .cursorrules as in NodeForge PRD.
Build for Simulator and report only when Loop Mode scoring works.
```

## Simulator (on Kolya only)

```bash
cd ~/Developer/EnglishOnSite   # or your real path
xcodebuild -scheme EnglishOnSite -destination 'platform=iOS Simulator,name=iPhone 16' build
```
