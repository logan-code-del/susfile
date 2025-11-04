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
        # Prefer environment variables if present, otherwise prompt interactively
        pw = os.environ.get('VIEWER_PASSWORD')
        if not pw:
            pw = getpass.getpass('Enter viewer password (will be stored in viewer/.env): ')
        duration = os.environ.get('VIEWER_DURATION', '30')
        ascii_seconds = os.environ.get('VIEWER_ASCII_SECONDS', '3')
        whitelist = os.environ.get('VIEWER_WHITELIST')
        if whitelist is None:
            whitelist = input('Comma-separated whitelist of GitHub usernames (leave blank for none): ').strip() or None

        write_env(viewer_dir, pw, duration, ascii_seconds, whitelist)

        # Install dependencies (unless disabled)
        if not args.no_install:
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
        else:
            # On most platforms `npm run start` will launch the electron app in the current session
            print('Starting npm/electron viewer... (Ctrl+C to stop)')
            run(['npm', 'run', 'start'], cwd=str(viewer_dir))


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


if __name__ == '__main__':
    main()
