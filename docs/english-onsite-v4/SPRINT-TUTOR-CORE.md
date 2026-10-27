# English Onsite v4 — Sprint: Tutor Learning Core

**Status:** Research kernel + drop-in protocol shipped in this repo. **Wire + Simulator on Mac «Kolya»** inside `EnglishOnSite` (Gemini already in Settings).

## Goal

Make **Репетитор** follow a science-based tutor↔student dialogue core (not free chat): task → graduated repair → reproduction → spaced miss bank.

## Docs

| File | Role |
|------|------|
| `LEARNING-CORE.md` | Product law / pedagogy |
| `TUTOR-DIALOGUE-PROTOCOL.md` | State machine + JSON contract |
| `RESEARCH-SOURCES.md` | Evidence bibliography (2020–2026 + foundations) |

## Drop-in files

| File | Action |
|------|--------|
| `DropIn/EnglishOnSiteTutor/TutorSystemPrompt.md` | Gemini system instruction |
| `DropIn/EnglishOnSiteTutor/TutorSessionEngine.swift` | Session engine + miss_bank spacing |
| `DropIn/EnglishOnSiteTutor/learning_core.json` | Machine config / sample can-dos |
| `DropIn/EnglishOnSiteTutor/fixtures/standup_repair_turn.json` | Eval fixture |

## Acceptance (Kolya)

1. Open Репетитор → start B1 standup can-do.  
2. Say a broken present-perfect line → tutor climbs repair ladder, asks re-say.  
3. Soft fail reproduction → “Let’s try again” (AVSpeech) + level +1.  
4. Success → back to task; miss logged for +1 day.  
5. Close → self-eval “Today I can…”.

## Out of scope this sprint

Full offline lesson bank generator, peer mode, App Store release.
