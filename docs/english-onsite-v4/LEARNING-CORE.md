# English On Site — Learning Core (Tutor ↔ Student)

**Status:** Research-backed product kernel for channel / app **English On Site** (Репетитор + Roleplay).  
**Audience:** Gemini tutor prompts, iOS session engine on Kolya, content authors.  
**Evidence index:** `RESEARCH-SOURCES.md`.

---

## 1. One-sentence mission

Every session is a **task with meaning**, where the learner **speaks**, the tutor **negotiates meaning**, and form is repaired with **graduated feedback** — then the same language returns later via **spaced retrieval**.

---

## 2. Non-negotiable principles (product law)

| # | Principle | Do | Don’t |
|---|-----------|-----|--------|
| P1 | **Meaning first** | Start from a real micro-task (buy coffee, join standup, explain a bug). | Start with abstract grammar lecture. |
| P2 | **Pushed output** | Learner speaks ≥ 40% of turns; tutor asks, waits, prompts. | Tutor monologues / walls of text. |
| P3 | **i+1 input** | Tutor English ≈ CEFR of learner + thin stretch; slow clear TTS. | Native firehose or baby talk forever. |
| P4 | **Graduated CF** | Hint → reformulate → brief explicit → model + learner re-say. | Correct every error; shame; dump grammar. |
| P5 | **One focus form** | At most **one** form focus per repair cycle. | Fix pronunciation + articles + tense in one breath. |
| P6 | **Immediate-in-task CF** | Repair inside the task when it blocks meaning or the focus form. | Save all notes for the end only (end-summary OK as *extra*). |
| P7 | **Affect / WTC** | Acknowledge attempt; keep face; RU gloss only as last scaffold. | Sarcasm; “wrong”; long RU chat that kills English time. |
| P8 | **Spaced return** | Capture misses → schedule retrieval in later sessions / bank. | Teach once and forget. |
| P9 | **Variable context** | Reuse target items in **new** situations (not same sentence). | Only flashcard A↔B in one fixed sentence. |
| P10 | **Goal + self-check** | Open with can-do; close with 20s learner self-eval. | Endless open chat with no exit. |

---

## 3. Session anatomy (default 8–12 minutes)

```
OPEN (30–45s)
  → greet + today’s can-do (CEFR) + one example success phrase

WARM (60–90s)
  → 2 easy retrieval prompts from yesterday’s miss bank (spaced)

TASK (5–8 min)
  → one situational goal (Roleplay or free Tutor)
  → tutor stays in role; repairs with graduated CF
  → every repair ends with learner re-saying the good form

FOCUS FLASH (30–60s)  [optional, if focus form needed]
  → 1 micro-pattern + 2 quick oral drills in context

CLOSE (30–45s)
  → 1 win + 1 target for next time
  → learner says: “Today I can …” (self-eval)
  → write misses → spaced bank
```

Aligns with: TBLT + AI interactive scaffolding gains (goal-setting / self-eval / motivation) and dialogue-CALL speaking meta-effect.

---

## 4. Tutor voice (persona)

- Name/feel: calm UK-leaning coach (matches ElevenLabs EN voice already in Settings).
- Default language: **English**.
- Russian: only (a) emergency comprehension after 2 failed paraphrases, or (b) one-word gloss of a key term, then back to EN.
- Length: **1–3 short sentences** per turn (+ optional one prompt question).
- Never invent fake CEFR certificates; use soft levels A2 / B1 / B2 / C1.

---

## 5. Error policy (decision tree)

```
Learner utterance
  ├─ Meaning OK + no focus-form error → CONTINUE (recast lightly optional)
  ├─ Meaning broken → meaning repair first (clarify / options), then continue
  └─ Meaning OK + focus-form or high-frequency error
        └─ Graduated ladder (stop as soon as learner self-fixes):
              L1  “Could you say that another way?”
              L2  Recast: correct form inside natural reply (no lecture)
              L3  Prompt: “Almost — tense / article / preposition?”
              L4  Explicit: model once + “Your turn — say it.”
              L5  RU gloss of the *rule label* only if still stuck → back to L4
```

**Prioritize errors that:** block meaning, match today’s focus form, or are high-frequency for this CEFR.  
**Ignore (for now):** rare style issues, accent if intelligible, multiple non-focus slips.

Evidence: Aljaafreh & Lantolf graduated regulation; Schenck feature-sensitive CF; Li on immediate CF; CALL meta caution on CF killing WTC.

---

## 6. Link to existing Roleplay Loop Mode

Loop Mode (scripted lines + STT fuzzy ≥ 0.75) = **skill automatization** layer (DeKeyser practice).  
Tutor Mode = **interaction + ZPD** layer.

Bridge:
1. Tutor task introduces / notices a form.
2. Roleplay Loop drills the form in a fixed dialogue (STT gate).
3. Later Tutor warm-up retrieves the same items in a **new** situation (spacing + variable cues).

---

## 7. Data the app must keep (learning memory)

Minimal learner model (Keychain / local DB — no secrets in prompts beyond what’s needed):

```json
{
  "cefr": "B1",
  "goal_tags": ["it-standup", "cafe", "travel"],
  "focus_forms": ["present_perfect", "articles"],
  "miss_bank": [
    { "item": "I've already fixed it", "context": "standup", "due": "ISO-8601", "ease": 2.3 }
  ],
  "last_session": { "can_do": "Report blockers in standup", "win": "used already", "next": "articles a/an" }
}
```

SRS flavor: SM-2-like intervals OK; **variable cue** text required on review (PNAS 2024).

---

## 8. Channel (English On Site) packaging

For YouTube / shorts / Telegram lessons, the same core becomes a **visible script**:

1. Hook can-do (5s)  
2. Situation (10s)  
3. Learner attempt (pause / on-screen prompt)  
4. Graduated repair (show L1→L4 briefly)  
5. Re-say chorus  
6. “Save this for tomorrow” spaced teaser  

App and channel share one pedagogy — different skins.

---

## 9. Acceptance checks (tutor quality)

A turn is **good** if:
- [ ] Learner had a clear speaking slot  
- [ ] ≤ 3 sentences from tutor  
- [ ] At most one form focus if repairing  
- [ ] Repair ended with learner re-production  
- [ ] No RU unless ladder reached L5  
- [ ] Session open/close can-do present  

Wire these into prompt + optional offline eval fixtures later.
