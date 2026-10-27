# Tutor Dialogue Protocol — English On Site

Machine-facing contract for the **Репетитор** tab (Gemini). Implements `LEARNING-CORE.md`.

---

## 1. Session state machine

```
idle
  → open
  → warm_retrieval      (0–2 items from miss_bank if due)
  → task_run            (main role / free talk)
       ⇄ repair         (nested; returns to task_run)
  → focus_flash         (optional)
  → close
  → persist             (update miss_bank, last_session)
  → idle
```

| State | Tutor goal | Exit when |
|-------|------------|-----------|
| `open` | State can-do + invite first speak | Learner greets / answers ready |
| `warm_retrieval` | Cue due item in **new** sentence | Item done or bank empty |
| `task_run` | Drive task toward can-do success | Goal met or timebox |
| `repair` | Graduated ladder L1–L5 | Learner re-says OK form |
| `focus_flash` | 1 pattern + 2 oral reps | 2 successful reps |
| `close` | Win + next + self-eval prompt | Learner self-eval captured |
| `persist` | App-only | Written |

---

## 2. Turn packet (app → model)

```json
{
  "protocol_version": 1,
  "phase": "task_run",
  "learner": {
    "cefr": "B1",
    "l1": "ru",
    "goal_tags": ["it-standup"],
    "focus_forms": ["present_perfect"],
    "miss_bank_due": [
      { "item": "I've already fixed it", "hint_context": "daily standup" }
    ]
  },
  "session": {
    "can_do": "Report what I finished and what's blocked in a standup",
    "minutes_left": 6,
    "repair_level": 0,
    "focus_form": "present_perfect",
    "last_tutor_move": "ask",
    "task_brief": "You are the team lead in a morning standup."
  },
  "learner_utterance": "I already fix the bug yesterday"
}
```

## 3. Turn packet (model → app)

Respond with **JSON only** (no markdown fences):

```json
{
  "phase": "repair",
  "repair_level": 2,
  "speak": "Yesterday — nice. I've already fixed the bug. Can you say that?",
  "speak_locale": "en",
  "expect_learner": "reproduction",
  "target_form": "I've already fixed the bug",
  "recast": "I've already fixed the bug",
  "log_miss": true,
  "miss_item": "I've already fixed it",
  "ui": {
    "coach_chip": "Present perfect + already",
    "show_ru_gloss": false
  },
  "session_patch": {
    "can_do_progress": 0.4
  },
  "end_session": false
}
```

### Field rules

| Field | Rule |
|-------|------|
| `speak` | 1–3 short sentences; TTS-friendly; no emoji spam |
| `speak_locale` | `en` default; `ru` only at repair_level ≥ 5 for a gloss, then next turn `en` |
| `repair_level` | 0 = none; 1–5 = ladder; drop to 0 after successful reproduction |
| `expect_learner` | `free` \| `reproduction` \| `self_eval` \| `yes_no` |
| `log_miss` | true → app schedules spaced review with **new** cue later |
| `end_session` | true only from `close` after self-eval |

---

## 4. Repair ladder (runtime)

| Level | Move | Example |
|-------|------|---------|
| 1 | Clarification / retry | “Say that again?” |
| 2 | Recast in reply | “Ah, you’ve **already fixed** it — good.” |
| 3 | Metalinguistic nudge | “Almost — we need *present perfect* with *already*.” |
| 4 | Model + push output | “Listen: *I’ve already fixed it.* Your turn.” |
| 5 | Tiny L1 gloss + model | “Это *present perfect*. *I’ve already fixed it.* Say it.” |

Never jump to 5 on first error. Never stay on 5 next turn if learner succeeded.

---

## 5. Integration with STT scoring

- **Roleplay Loop Mode:** keep `DialogueFuzzyMatcher` (≥ 0.75) for scripted lines.  
- **Tutor Mode:** do **not** hard-fail on fuzzy score. Use Gemini judgment + optional soft match when `expect_learner == reproduction` against `target_form` (threshold **0.70** OK).  
- UI “Let’s try again” (AVSpeech) only when `expect_learner == reproduction` and soft match fails — then bump `repair_level` +1 (cap 5).

---

## 6. Wire on Kolya (EnglishOnSite)

1. Copy `DropIn/EnglishOnSiteTutor/*` into the app.  
2. Load `TutorSystemPrompt.md` as Gemini system instruction.  
3. Each mic result → build turn packet → Gemini → parse JSON → ElevenLabs/AVSpeech `speak` → update phase.  
4. On `log_miss` → miss_bank with due date (1d → 3d → 7d → 21d default).  
5. Settings already have Gemini + ElevenLabs Keychain — reuse.

Owner paste for Kolya Cursor:

```text
Open EnglishOnSite. Implement Tutor Dialogue Protocol from docs/english-onsite-v4:
- LEARNING-CORE + TUTOR-DIALOGUE-PROTOCOL
- Use DropIn/EnglishOnSiteTutor prompt + TutorSessionEngine stub
- Gemini JSON turns; graduated repair L1–L5; miss_bank spacing
- Keep Roleplay STT gate separate (0.75); tutor reproduction soft 0.70
Build Simulator; verify one standup can-do session open→task→repair→close.
```
