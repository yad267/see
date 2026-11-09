#!/usr/bin/env bash
# Apply bulk banks + UI from AgentStores artifacts into Languages-on-site checkout.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Prefer explicit env, else common Kolya paths.
if [[ -n "${LOS_ROOT:-}" ]]; then
  ROOT="$LOS_ROOT"
elif [[ -d "$HOME/Developer/Languages-on-site/EnglishOnSite" ]]; then
  ROOT="$HOME/Developer/Languages-on-site"
elif [[ -d "$HOME/Developer/EnglishOnSite/EnglishOnSite" ]]; then
  ROOT="$HOME/Developer/EnglishOnSite"
elif [[ -d "$HOME/see/../Languages-on-site/EnglishOnSite" ]]; then
  ROOT="$(cd "$HOME/see/../Languages-on-site" && pwd)"
else
  echo "ERROR: set LOS_ROOT to Languages-on-site repo root" >&2
  exit 1
fi

EOS="$ROOT/EnglishOnSite"
test -d "$EOS" || { echo "ERROR: missing $EOS" >&2; exit 1; }

echo "Applying into: $ROOT"
cp -v "$SCRIPT_DIR/Resources/learning_words_v1.json" "$EOS/Resources/learning_words_v1.json"
cp -v "$SCRIPT_DIR/Resources/learning_phrasals_site_v1.json" "$EOS/Resources/learning_phrasals_site_v1.json"
cp -v "$SCRIPT_DIR/Services/LearningBankStore.swift" "$EOS/Services/LearningBankStore.swift"
cp -v "$SCRIPT_DIR/Services/GeminiSiteCoachService.swift" "$EOS/Services/GeminiSiteCoachService.swift"
cp -v "$SCRIPT_DIR/Views/LearningBankView.swift" "$EOS/Views/LearningBankView.swift"
cp -v "$SCRIPT_DIR/Views/LibraryView.swift" "$EOS/Views/LibraryView.swift"

echo "Done. Rebuild the iOS app in Xcode."
echo "Then: Мои фразы / Учить → «Добавить фразовые глаголы»."
