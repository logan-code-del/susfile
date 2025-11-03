Susfile viewer (local)

This is a small Electron wrapper that opens `viewer.html` in a popup window and prevents the window from being closed until either:

- the built-in timer expires (default 30s), or
- the correct password is entered (default password in this demo: `letmein`)

Important notes
- This app is intended to run locally on machines you control. It will open a GUI window and therefore requires a desktop environment.
- The process can always be terminated by killing it from Task Manager (Windows) / Activity Monitor (macOS) / kill command (Linux). That is the supported method for forcing a stop.

Run locally
1. Install dependencies:

```bash
cd viewer
npm ci
```

2. Start the viewer:

```bash
npm start
```

Customization
- Change the timer duration in `viewer.html` (variable `duration`) or implement a secure password mechanism.
- For production use, replace the demo `letmein` password with a secure method and consider building a packaged app.

Self-hosted runner note
- The workflow `/.github/workflows/viewer_dispatch.yml` can dispatch this app on a self-hosted runner with a desktop session. GitHub-hosted runners cannot show GUI windows.

Using repository secrets (recommended)
- To prevent secret values from being stored in the repository and to restrict who can change them, use GitHub repository secrets.
- The `viewer_dispatch` workflow will create a `viewer/.env` from the following repo secrets when it runs on a self-hosted runner:
	- `VIEWER_PASSWORD` — password required to unlock (if not whitelisted)
	- `VIEWER_DURATION` — timer duration in seconds (default 30)
	- `VIEWER_ASCII_SECONDS` — how many seconds to show the ASCII overlay before revealing the UI (default 3)
	- `VIEWER_WHITELIST` — comma-separated list of GitHub usernames allowed as whitelisted users (e.g. `alice,bob`)

Notes:
- Only users with repository Settings -> Secrets permissions (typically repo admins) can add or change these secrets. The values are not stored in the repository.
- The workflow writes them to `viewer/.env` at runtime on the self-hosted runner, so they are available to the Electron process started by the workflow. They are not checked into source control by the workflow.

