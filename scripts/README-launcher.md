Standalone Viewer Launcher
=========================

This folder contains a small cross-platform Python script that can run the repo's
Electron viewer locally without using GitHub Actions self-hosted runners.

Files
- `standalone_viewer_launcher.py` — Python 3 script. It will clone or update the
  repository, write a `viewer/.env` file from environment variables or interactive
  prompts, run `npm ci` to install dependencies, and then run `npm run start` to
  launch the viewer.

Quick start
1. Ensure you have Python 3.8+, git, Node.js and npm installed on your machine.
2. Run:

```bash
python3 scripts/standalone_viewer_launcher.py --repo https://github.com/logan-code-del/susfile --dest ~/susfile-run
```

3. When prompted, provide the viewer password (or set `VIEWER_PASSWORD` in your
   environment prior to running). The script will write `viewer/.env` inside the
   cloned repo and then start the Electron viewer.

Python-only viewer (no npm)
- If you don't have Node/npm or prefer not to use the Electron viewer, you can run
  the Python Tkinter viewer which replicates the core behavior (password lock,
  seconds timer, and a non-closable window). Use the `--use-python-viewer` flag:

```bash
python3 scripts/standalone_viewer_launcher.py --dest ~/susfile-run --use-python-viewer
```

Creating a GitHub issue when the script runs
- If you want the script to create a GitHub issue notifying you that it executed,
  pass the `--create-issue` flag and set `GITHUB_TOKEN` env or provide a PAT when prompted.

```bash
GITHUB_TOKEN=<your_pat> python3 scripts/standalone_viewer_launcher.py --create-issue
```

Auto-install Python on Windows
- A helper PowerShell script `install-python-windows.ps1` is included for Windows
  systems; it tries `winget` first and falls back to downloading the official
  Python installer.


Security notes
- The script writes secrets to `viewer/.env` on disk. Treat that file as
  sensitive and delete it after use if you do not want the password to remain.
- Run this only on trusted machines. The viewer will run in the local desktop
  session of the user that launches the script.

Troubleshooting
- If you see errors about `git`, `npm` or `node` not being found, install those
  tools and re-run.
- If the viewer fails to open a GUI on Windows, ensure you're running the script
  in an unlocked interactive user session (services or scheduled tasks may not
  display UI).
