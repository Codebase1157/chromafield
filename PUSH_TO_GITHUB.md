# Putting this on GitHub

This folder is a complete, ready-to-push repository. Nothing needs editing.

## 1. Create the empty repository

Go to <https://github.com/new> and create:

- **Owner:** `Codebase1157`
- **Name:** `ChromaField`
- **Visibility:** Public
- **Do not** tick "Add a README", "Add .gitignore" or "Choose a license" —
  those files are already here, and an auto-generated one would collide on the
  first push.

## 2. Push

From inside this folder:

```bash
bash push_to_github.sh
```

Or by hand:

```bash
git init -b main
git add -A
git commit -m "ChromaField reproduction package"
git remote add origin https://github.com/Codebase1157/ChromaField.git
git push -u origin main
```

If GitHub asks for a password, it wants a **personal access token**, not your
account password: <https://github.com/settings/tokens> → "Generate new token
(classic)" → tick `repo` → use the token as the password. Or use the GitHub
CLI, which handles this for you:

```bash
gh auth login
gh repo create Codebase1157/ChromaField --public --source=. --push
```

## 3. Check it landed

- The Colab badge at the top of `README.md` should open the notebook.
- The **Actions** tab should show the `verify artefacts` workflow running. It
  re-runs `verify_artifact.py`, `eval/aggregate.py` and `stats/run_all.py`
  against the committed predictions and asserts the archive is byte-identical
  afterwards. It takes about a minute and should pass.

## Notes on size

The repository is about 127 MB, the largest single file 8.6 MB. That is
comfortably inside GitHub's limits (100 MB per file, warnings above 1 GB per
repository), so Git LFS is not needed. If you later add more runs under
`artifacts/`, consider LFS for the `*.pt` checkpoints:

```bash
git lfs install
git lfs track "artifacts/**/*.pt"
git add .gitattributes
```

## If the push is rejected as too large

Only the checkpoints are bulky. To publish the package without them:

```bash
git rm -r --cached artifacts/*/checkpoints
echo "artifacts/*/checkpoints/" >> .gitignore
git commit -m "Exclude checkpoints from the repository"
```

`verify_artifact.py` will then report those files as missing, which is correct
and honest — note it in the README if you do this, and host the weights
somewhere with a stable link instead.
