# susfile

Susfile is a repository that contains the CNARS license and tooling to manage
commercial permission requests, plus a local viewer app and helper scripts to
run a short, non-dismissible viewer UI for maintainers.

This repository contains:
- `LICENSE.md` — the CNARS license text for this project
- `.github/` — GitHub Actions workflows and issue templates for commercial requests
- `viewer/` — Electron-based viewer app that opens a popup and requires a password or timer to close
- `scripts/` — helper scripts (Windows HTA, PowerShell wrappers, Python standalone launcher) to run the viewer outside GitHub Actions

Security note
- This repository must never contain secrets (Personal Access Tokens, passwords,
  private keys). Store secrets in GitHub repository secrets or a private secrets
  repository (example: `logan-code-del/secrets-repo`) and use short-lived tokens.

Quick start (local run)
1. Ensure you have a desktop session (on Windows or Linux with X11/Wayland) and Python 3.8+ installed.
2. For Windows, register the custom protocol once:

```powershell
cd scripts
powershell -ExecutionPolicy Bypass -File .\register-protocol-windows.ps1
```

3. Set a GitHub token in your session (temporary):

PowerShell (session):
```powershell
#$env:GITHUB_TOKEN = 'ghp_...'
```

4. Run the HTA or clickable HTML locally and click to launch the viewer, or run the PowerShell wrapper:

```powershell
# Run wrapper (will ensure Python is installed and start the viewer)
.
\scripts\win-launcher.ps1 -Dest "$env:USERPROFILE\susfile-run" -UsePythonViewer -Cleanup -SecretsRepo 'logan-code-del/secrets-repo'
```

See `scripts/README-scripts.md` for full details.
