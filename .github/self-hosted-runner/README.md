Self-hosted runner setup for "viewer_dispatch" workflow

This directory contains helper scripts and documentation to install and run a GitHub Actions self-hosted runner that can execute the `viewer_dispatch` workflow (it must run on a machine with a desktop session to display the Electron viewer).

Security note
- Only run this on a machine you control and trust. The runner will execute repository workflows and may receive repository secrets via job env. Treat it as a sensitive machine.

Pre-flight
- Create a repository registration token (temporary) from GitHub UI (Settings → Actions → Runners → Add runner → Generate token) or use the GitHub REST API to create a registration token. The token is short-lived.
- On the runner machine, install required packages (curl, tar, sudo) and ensure you have a desktop session (X11/Wayland) running where GUI apps may open.

Quick install (recommended)
1. Copy this repository to the runner machine or clone it.
2. Set environment variables (example):

```bash
export RUNNER_NAME="susfile-viewer-runner"
export RUNNER_LABELS="self-hosted,viewer" # labels to attach to the runner; workflows can target these
export RUNNER_TOKEN="<the registration token from GitHub>"
export GITHUB_URL="https://github.com/<owner>/<repo>"
export RUNNER_VERSION="2.308.0" # optional, defaults to that version
```

3. Run the installer script (may require sudo for service install):

```bash
cd .github/self-hosted-runner
# You must have RUNNER_TOKEN, RUNNER_NAME and GITHUB_URL set in the environment
./install-runner.sh
```

This will download the runner, register it with your repository, and start it in the foreground. To run as a service, follow the systemd instructions below or use the `run-as-service.sh` helper.

Uninstall / cleanup
- To remove the runner, run `./config.sh remove --unattended --token <token>` inside the runner directory, or use the GitHub UI to remove the runner. Then stop and remove any systemd service if you created one.

Systemd service (example)
- A sample systemd unit is provided in `actions.runner.service`. Copy it to `/etc/systemd/system/actions.runner.service`, update the `WorkingDirectory` and `User` entries, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable actions.runner
sudo systemctl start actions.runner
```

Important: when registering the runner the registration token is short-lived; use the GitHub UI to generate it right before running the register script.

Windows runner
- This repository includes a PowerShell helper `install-runner-windows.ps1` to set up a Windows self-hosted runner interactively.
- On the Windows machine you want to use as the runner:

```powershell
# In an elevated PowerShell prompt (if you plan to run as service), set these env vars first:
$env:GITHUB_URL = 'https://github.com/<owner>/<repo>'
$env:RUNNER_TOKEN = '<registration token from GitHub>'
$env:RUNNER_NAME = 'susfile-windows-runner'
$env:RUNNER_LABELS = 'self-hosted,viewer'
cd .github\self-hosted-runner
.\install-runner-windows.ps1
```

- The script will download the runner release, configure it with `config.cmd`, and start `run.cmd` interactively. To run the runner as a Windows Service you can use NSSM (https://nssm.cc/) or the Windows Service Wrapper of your choice — the script does not install a service automatically.

