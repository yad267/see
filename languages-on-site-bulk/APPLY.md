# How files get from `see` → Languages-on-site (restored flow)

## Old mechanism (what worked before)

Cloud agents wrote learning CSVs / packs to **`/opt/cursor/artifacts/`**.
Cursor synced that tree to Kolya’s Mac under AgentStores:

`~/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/<bcId>/files/artifacts/`

No `git push` to `Languages-on-site` was required (and this cloud bot still has **no push** there — 403).

Code edits historically also used canvas copy-paste into Mac Composer, or later a **My Machines** worker on `~/Developer/Languages-on-site` / `EnglishOnSite`.

## Restored today

Bulk package is published again to:

`/opt/cursor/artifacts/languages-on-site-bulk/`

Contents: 3000-word JSON, 143 phrasals JSON, Swift UI/services, `apply-to-los.sh`, `MANIFEST.txt`.

Also in git: `languages-on-site-bulk/` on branch `cursor/learning-bank-bulk-6ccf` (PR #10).

## Automatic apply (pick one)

### A) AgentStores + one script on Mac (closest to old flow)

1. Wait for AgentStores sync of this run (`bc-01a08d3b-…` / ОБОВСЕМ) or open this chat on desktop so artifacts refresh.
2. On Kolya Mac:

```bash
ART="$HOME/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-01a08d3b-30fd-7a5d-a867-726d53026ccf/files/artifacts/languages-on-site-bulk"
# if bcId folder differs, find it:
# find "$HOME/Library/Application Support/Cursor/AgentStores" -type d -name 'languages-on-site-bulk' 2>/dev/null
bash "$ART/apply-to-los.sh"
```

3. Rebuild iOS in Xcode → «Добавить фразовые глаголы».

### B) New Agent on My Machines (fully hands-off once worker is up)

1. On Kolya: `agent worker start --name "Languages-on-site" --worker-dir "$HOME/Developer/Languages-on-site"`
2. New Cloud Agent → run on that machine → paste:

```
Apply the bulk pack from AgentStores or from see branch cursor/learning-bank-bulk-6ccf path languages-on-site-bulk/ into this checkout's EnglishOnSite/ using apply-to-los.sh (or copy the listed files). Commit on branch cursor/learning-bank-bulk-6ccf and confirm counts: 3000 words, 143 phrasals.
```

### C) Not available from this cloud VM

`git push origin` to `yad267/Languages-on-site` → **403** (bot has pull:false, push:false). Do not rely on CI sync — neither repo has a workflow for this.
