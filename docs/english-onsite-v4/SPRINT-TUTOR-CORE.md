# English Onsite v4 — Sprint: Tutor Immersion Core

**Status:** Drop-in ready. Wire on Mac «Kolya» into `EnglishOnSite` Репетитор.

## Goal

Репетитор = Irish-site immersion coach (gate / foreman / PPE), not free chat:
scenario → oral loop → graduated repair → predictive miss bank.

## Files

| Path | Role |
|------|------|
| `LEARNING-CORE.md` | Pedagogy law |
| `IMMERSION-STACK.md` | DLI/AFRL → product map |
| `TUTOR-DIALOGUE-PROTOCOL.md` | JSON state machine |
| `RESEARCH-SOURCES.md` | Evidence |
| `DropIn/EnglishOnSiteTutor/TutorSystemPrompt.md` | Gemini system |
| `DropIn/EnglishOnSiteTutor/TutorSessionEngine.swift` | Session + pack loader |
| `DropIn/EnglishOnSiteTutor/PredictiveReviewEngine.swift` | Decay × frequency × fails |
| `DropIn/EnglishOnSiteTutor/scenarios/irish_site_v1.json` | Safe Pass, put, cabin, PPE |
| `DropIn/EnglishOnSiteTutor/learning_core.json` | Machine config v2 |

## Kolya acceptance

1. Репетитор → scenario **Ворота и Safe Pass**.  
2. Broken line → repair ladder → re-say.  
3. Fail reproduction → AVSpeech “Let’s try again”.  
4. Next day warm-up pulls high-frequency miss first.  
5. Scenario **put phrasals** uses SAY IT: *Put up the cable tray and put back your tools.*

## Assumptions locked (no owner questions)

- Audience: RU, Irish sites  
- No VR this sprint  
- Gemini + ElevenLabs Keychain already in Settings  
- ILR-lite labels only (not official testing)
