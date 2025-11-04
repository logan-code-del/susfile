#!/usr/bin/env python3
"""
Standalone Viewer Launcher

This script is intended to be run locally (outside the repository) to fetch the
repository, prepare runtime configuration, and start the Electron viewer without
using a GitHub Actions self-hosted runner.

Usage examples:
  python3 standalone_viewer_launcher.py
  python3 standalone_viewer_launcher.py --repo https://github.com/logan-code-del/susfile --dest /tmp/susfile-run

Requirements:
- Python 3.8+
- git installed and on PATH
- Node.js + npm installed and on PATH (the viewer is an Electron app)

Security notes:
- This script will write a `viewer/.env` file in the cloned repository containing
  any values you provide (passwords). Treat the machine as trusted and delete
  the `.env` file after use if required.
"""
from __future__ import annotations
import argparse
import getpass
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_program(name: str) -> bool:
    return shutil.which(name) is not None


def run(cmd, cwd=None, env=None):
    print(f"-> Running: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=cwd, env=env)


def clone_or_update(repo: str, dest: Path, branch: str | None):
    if dest.exists() and (dest / '.git').exists():
        print(f"Repository already exists at {dest}, performing git fetch && reset...")
        run(['git', 'fetch', '--all'], cwd=str(dest))
        if branch:
            run(['git', 'checkout', branch], cwd=str(dest))
        run(['git', 'reset', '--hard', 'origin/' + (branch or 'HEAD')], cwd=str(dest))
    else:
        clone_cmd = ['git', 'clone', '--depth', '1']
        if branch:
            clone_cmd += ['--branch', branch]
        clone_cmd += [repo, str(dest)]
        run(clone_cmd)


def write_env(viewer_dir: Path, password: str, duration: str, ascii_seconds: str, whitelist: str | None):
    env_path = viewer_dir / '.env'
    print(f"Writing env to {env_path} (keep this file secure)")
    lines = [f"PASSWORD={password}", f"DURATION={duration}", f"ASCII_SECONDS={ascii_seconds}"]
    if whitelist is not None:
        lines.append(f"WHITELIST={whitelist}")
    env_path.write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='https://github.com/logan-code-del/susfile', help='Git URL of the repo')
    parser.add_argument('--branch', default=None, help='Branch to checkout')
    parser.add_argument('--dest', default=None, help='Destination directory to clone into (default: ~/.local/susfile_viewer_run)')
    parser.add_argument('--viewer-subdir', default='viewer', help='Path under the repo that contains the viewer app')
    parser.add_argument('--no-install', action='store_true', help='Skip npm install (assume dependencies are present)')
    parser.add_argument('--use-python-viewer', action='store_true', help='Run the bundled Python Tkinter viewer instead of the npm/electron viewer')
    parser.add_argument('--create-issue', action='store_true', help='Create a GitHub issue to notify that the script ran (requires GITHUB_TOKEN env or prompt)')
    parser.add_argument('--cleanup', action='store_true', help='Remove viewer/.env after the viewer exits')
    parser.add_argument('--verify-ref', default=None, help='A git tag or commit hash to verify after cloning (integrity check)')
    parser.add_argument('--secrets-repo', default='logan-code-del/secrets-repo/', help='Optional owner/repo where a secrets JSON file is stored (e.g. owner/secrets-repo)')
    parser.add_argument('--secrets-path', default='secrets/viewer_config.json', help='Path inside secrets repo to the JSON config file')
    parser.add_argument('--install-node', action='store_true', help='On Windows, try to install Node.js via winget if missing')
    args = parser.parse_args()

    if not check_program('git'):
        print('git is required but not found on PATH. Install git and retry.')
        sys.exit(1)

    if not check_program('node') or not check_program('npm'):
        print('Warning: node/npm not found on PATH. The viewer requires Node/Electron to run.')
        print('Install Node.js and npm for your platform, or use an environment that has them.')

    dest = Path(args.dest) if args.dest else (Path.home() / '.local' / 'susfile_viewer_run')
    viewer_dir = dest / args.viewer_subdir

    try:
        dest.mkdir(parents=True, exist_ok=True)
        clone_or_update(args.repo, dest, args.branch)

        # Ensure viewer dir exists
        if not viewer_dir.exists():
            print(f'Error: expected viewer dir {viewer_dir} not found in repo. Aborting.')
            sys.exit(2)

        # Prepare runtime config
        # Fetch secrets from a separate secrets repo if requested (this requires a token)
        pw = None
        whitelist = None
        duration = os.environ.get('VIEWER_DURATION', '30')
        ascii_seconds = os.environ.get('VIEWER_ASCII_SECONDS', '3')
        if args.secrets_repo:
            token = os.environ.get('GITHUB_TOKEN')
            if not token:
                token = getpass.getpass('Enter a GitHub Personal Access Token (with repo read access to the secrets repo): ')
            if not token:
                print('No token provided; cannot fetch secrets. Aborting to avoid interactive secret entry.')
                sys.exit(4)
            try:
                cfg = fetch_secrets_from_repo(args.secrets_repo, args.secrets_path, token)
                pw = cfg.get('PASSWORD')
                whitelist = cfg.get('WHITELIST')
                # allow duration/ascii override from secrets file if present
                duration = str(cfg.get('DURATION', duration))
                ascii_seconds = str(cfg.get('ASCII_SECONDS', ascii_seconds))
                print('Fetched viewer config from secrets repo')
            except Exception as e:
                print('Failed to fetch secrets from repo:', e)
                sys.exit(5)
        else:
            # Do not allow interactive password entry if secrets_repo is not used
            pw = os.environ.get('VIEWER_PASSWORD')
            whitelist = os.environ.get('VIEWER_WHITELIST')
            if not pw:
                print('No viewer password provided via environment and no secrets repo configured. Aborting.')
                sys.exit(6)

        write_env(viewer_dir, pw, duration, ascii_seconds, whitelist)

        # Install dependencies (unless disabled)
        if not args.no_install:
            # Optionally auto-install Node on Windows using winget
            if sys.platform.startswith('win') and args.install_node and not check_program('node'):
                print('Attempting to install Node.js via winget...')
                try:
                    subprocess.check_call(['winget', 'install', '--id', 'OpenJS.NodeJS.LTS', '--scope', 'user', '-e'])
                except Exception as e:
                    print('winget install failed or winget not available:', e)
            if not check_program('npm'):
                print('npm not found; cannot install dependencies. If dependencies are already installed, re-run with --no-install')
                sys.exit(3)
            run(['npm', 'ci'], cwd=str(viewer_dir))

        # Start the viewer
        if args.use_python_viewer or not check_program('npm'):
            # Use the local python Tkinter viewer bundled with these scripts
            viewer_script = Path(__file__).resolve().parent / 'python_viewer.py'
            if not viewer_script.exists():
                print(f'Python viewer not found at {viewer_script}; cannot start python viewer')
                sys.exit(4)
            print('Starting Python Tkinter viewer... (Ctrl+C to stop; use Task Manager to kill process)')
            # Launch in a child process so the launcher can continue to create the GitHub issue if requested
            proc = subprocess.Popen([sys.executable, str(viewer_script),
                                     '--env', str(viewer_dir / '.env')])
            # Create GitHub issue if requested
            if args.create_issue:
                token = os.environ.get('GITHUB_TOKEN')
                if not token:
                    token = getpass.getpass('Enter a GitHub Personal Access Token (repo scope) to create an issue, or leave blank to skip: ')
                if token:
                    # repo arg may be full url like https://github.com/owner/repo
                    repo_arg = args.repo
                    # extract owner/repo
                    if repo_arg.endswith('.git'):
                        repo_arg = repo_arg[:-4]
                    if repo_arg.startswith('http'):
                        parts = repo_arg.rstrip('/').split('/')
                        owner_repo = '/'.join(parts[-2:])
                    else:
                        owner_repo = repo_arg
                    try:
                        create_github_issue(owner_repo, token, 'Standalone viewer launched', 'The standalone viewer launcher was executed on a machine.')
                        print('GitHub issue created.')
                    except Exception as e:
                        print('Failed to create GitHub issue:', e)
            # Wait for the viewer process to exit
            proc.wait()
            if args.cleanup:
                try:
                    (viewer_dir / '.env').unlink()
                    print('Cleaned up viewer/.env')
                except Exception as e:
                    print('Failed to remove viewer/.env:', e)
        else:
            # On most platforms `npm run start` will launch the electron app in the current session
            print('Starting npm/electron viewer... (Ctrl+C to stop)')
            run(['npm', 'run', 'start'], cwd=str(viewer_dir))
            if args.cleanup:
                try:
                    (viewer_dir / '.env').unlink()
                    print('Cleaned up viewer/.env')
                except Exception as e:
                    print('Failed to remove viewer/.env:', e)


    except subprocess.CalledProcessError as e:
        print('\nProcess failed with return code', e.returncode)
        print('Command:', e.cmd)
        sys.exit(e.returncode)


def create_github_issue(owner_repo: str, token: str, title: str, body: str):
    """Create a GitHub issue in owner/repo using a personal access token."""
    import json
    import urllib.request
    api = f'https://api.github.com/repos/{owner_repo}/issues'
    data = json.dumps({'title': title, 'body': body}).encode('utf-8')
    req = urllib.request.Request(api, data=data, headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'standalone-viewer-launcher'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status >= 200 and resp.status < 300:
            return json.load(resp)
        else:
            raise RuntimeError(f'GitHub API returned status {resp.status}')


def fetch_secrets_from_repo(owner_repo: str, path: str, token: str) -> dict:
    """Fetch a JSON file from a repository's contents API and return parsed JSON.

    owner_repo should be 'owner/repo'. Path is the file path in the repo.
    Requires a PAT with repo read access if the repo is private.
    """
    import base64, json, urllib.request
    api = f'https://api.github.com/repos/{owner_repo}/contents/{path}'
    req = urllib.request.Request(api, headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'standalone-viewer-launcher'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status >= 200 and resp.status < 300:
            data = json.load(resp)
            if data.get('encoding') == 'base64' and 'content' in data:
                raw = base64.b64decode(data['content'])
                return json.loads(raw.decode('utf-8'))
            else:
                raise RuntimeError('Unexpected content format from GitHub API')
        else:
            raise RuntimeError(f'GitHub API returned status {resp.status}')


def verify_git_ref(dest: Path, ref: str) -> bool:
    """Verify the checked out HEAD matches the given ref (commit hash or tag).
    Returns True if match, False otherwise.
    """
    try:
        # Resolve local HEAD
        local_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=str(dest)).decode().strip()
        # Try to resolve the provided ref to a commit
        target = subprocess.check_output(['git', 'rev-parse', ref], cwd=str(dest)).decode().strip()
        return local_head == target
    except Exception:
        return False


if __name__ == '__main__':
    main()
