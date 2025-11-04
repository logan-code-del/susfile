DO NOT STORE SECRETS IN THE REPOSITORY
=====================================

This repository previously contained a GitHub Personal Access Token (PAT) in
files under `scripts/` which triggered GitHub push protection. Secrets must not
be committed to Git. Follow the steps below to remediate and avoid future
exposure.

Immediate actions (do these now)
1. Revoke the exposed token in GitHub immediately (Settings → Developer settings → Personal access tokens → revoke the token).
2. Remove secret-containing files from your local working tree and replace them with templates (we created `scripts/TEMPLATE_new.env`).

Removing secrets from git history
- To fully remove secrets from the repository history you must rewrite history and force-push. Use one of the recommended tools:

Option A — git-filter-repo (recommended):

  # install: pip install git-filter-repo
  git clone --mirror https://github.com/youruser/susfile.git
  cd susfile.git
  git filter-repo --invert-paths --path scripts/new.env --path scripts/temp_run.ps1
  git push --force --mirror https://github.com/youruser/susfile.git

Option B — BFG Repo-Cleaner:

  # download bfg jar, then
  git clone --mirror https://github.com/youruser/susfile.git
  java -jar bfg.jar --delete-files scripts/new.env,scripts/temp_run.ps1 susfile.git
  cd susfile.git
  git reflog expire --expire=now --all && git gc --prune=now --aggressive
  git push --force --mirror

After history rewrite
- If GitHub push protection still blocks, use the repository Security → Secret scanning → Unblock link shown in the push error to confirm you’ve remediated and then push again. You may need to contact GitHub Support if automated unblocking is unavailable.

Prevention
- Never commit tokens. Use repository secrets (Settings → Secrets and variables → Actions) or a private secrets repo and fetch at runtime with a PAT that you control.
- Add entries to `.gitignore` for local env files, e.g. `scripts/*.env`.
- Use pre-commit hooks that scan for secrets (git-secrets, pre-commit hooks) to block accidental commits.

If you want, I can:
- Add a `.gitignore` entry and a small pre-commit hook to block typical secret patterns.
- Help run the git-filter-repo or BFG steps here (I can prepare the exact commands and patches; you must run them locally because they rewrite history and require credentials).
