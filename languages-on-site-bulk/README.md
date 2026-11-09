# Language Insight bulk material (9 Nov 2026)

Apply into `yad267/Languages-on-site` (paths under `EnglishOnSite/`):

| This package | Target |
|---|---|
| `Resources/learning_words_v1.json` | `EnglishOnSite/Resources/learning_words_v1.json` (**3000** words; 300 with RU) |
| `Resources/learning_phrasals_site_v1.json` | `EnglishOnSite/Resources/learning_phrasals_site_v1.json` (**143** phrasals) |
| `Services/LearningBankStore.swift` | seed button + daily drip |
| `Views/LearningBankView.swift` | «Добавить фразовые глаголы» |
| `Views/LibraryView.swift` | same button on «Мои фразы» |
| `Services/GeminiSiteCoachService.swift` | prompt: prefer core-3000 + phrasals |

Local commit on LOS clone (if you have push rights): branch `cursor/learning-bank-bulk-6ccf` at `/tmp/Languages-on-site` (commit `c4f0ce1`).

Tonight: rebuild iOS app; optional re-upload «ТОП 3000» PDF to fill remaining RU.
