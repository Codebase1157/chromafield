#!/usr/bin/env bash
# Push this folder to github.com/Codebase1157/ChromaField.
# Create the empty repository first; see PUSH_TO_GITHUB.md.
set -euo pipefail

OWNER="${OWNER:-Codebase1157}"
REPO="${REPO:-ChromaField}"
BRANCH="${BRANCH:-main}"
REMOTE="https://github.com/${OWNER}/${REPO}.git"

cd "$(dirname "$0")"

if [ ! -d .git ]; then
  git init -q -b "$BRANCH"
fi

git add -A
if git diff --cached --quiet; then
  echo "nothing to commit; the tree is already committed"
else
  git commit -q -m "ChromaField reproduction package: notebook, one full three-seed run, CI checks"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE"
else
  git remote add origin "$REMOTE"
fi

echo "pushing $(git rev-list --count HEAD) commit(s), $(git ls-files | wc -l) files to $REMOTE"
git push -u origin "$BRANCH"

cat <<MSG

Done. Next:
  repository : https://github.com/${OWNER}/${REPO}
  notebook   : https://colab.research.google.com/github/${OWNER}/${REPO}/blob/${BRANCH}/notebooks/chromafield_artifacts.ipynb
  CI         : https://github.com/${OWNER}/${REPO}/actions
MSG
