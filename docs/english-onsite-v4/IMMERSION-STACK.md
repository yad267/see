# English On Site — Immersion Stack (Linguist Next–lite)

What we build **now** from public military / intel training practice (DLI, CIA ILI, AFRL Linguist Next), without VR hardware.

## Assumptions (locked for this build)

| Decision | Value |
|----------|--------|
| Audience | RU L1 adults on Irish construction sites |
| Surface | Репетитор tab (+ SAY IT lines shared with lessons) |
| Voice | Existing Gemini + ElevenLabs + SFSpeech |
| VR/AR | Deferred — dialogue + audio immersion first |
| Measure | ILR-lite can-do (0+…2), not exam certificates |

## Stack layers

```
1. SCENARIO PACK     irish_site_v1.json
   gate / Safe Pass / foreman put-phrasals / cabin briefing / PPE

2. CAN-DO + ROLE     task_brief + tutor_role (gate_security|foreman|supervisor)

3. ORAL LOOP         speak → STT → graduated repair → re-say (SAY IT)

4. PREDICTIVE REVIEW decay × site frequency × fails
   PredictiveReviewEngine (AFRL-inspired lite)

5. TUTOR AGENT       TutorSystemPrompt.md + TutorSessionEngine
```

## Map from “спецшколы” → product

| Their practice | Our module |
|----------------|------------|
| Scenario / mission talk | `scenarios/irish_site_v1.json` |
| High speaking time | Репетитор JSON turns + SAY IT |
| Graduated coaching | repair L1–L5 |
| Predictive / personalized review | `PredictiveReviewEngine` |
| Authentic materials | Site lexis from your lessons (Safe Pass, cabin, cable tray) |
| VR immersion | Later: same scenarios as XR skins |

## Wire order on Kolya

1. Bundle `irish_site_v1.json` + tutor drop-in.  
2. Репетитор picker → scenario id → `TutorSessionConfig.fromIrishScenario`.  
3. Mic → `makeRequest` → Gemini → `apply` → TTS.  
4. Reproduction fail → AVSpeech “Let’s try again” + `bumpRepairAfterFailedReproduction`.  
5. Pass → `markReproductionSuccess`.  
6. Persist `learner.missBank` locally.

## Out of scope now

Full AFRL cognitive model, Oculus scenes, classified tradecraft content, peer VR.
