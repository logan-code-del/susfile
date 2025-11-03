#!/usr/bin/env bash
set -euo pipefail

# install-runner.sh
# Usage: set RUNNER_TOKEN, RUNNER_NAME, GITHUB_URL, optionally RUNNER_LABELS and RUNNER_VERSION

RUNNER_NAME=${RUNNER_NAME:-susfile-runner}
RUNNER_LABELS=${RUNNER_LABELS:-self-hosted,viewer}
GITHUB_URL=${GITHUB_URL:-}
if [ -z "$GITHUB_URL" ]; then
  echo "GITHUB_URL not set. Example: https://github.com/<owner>/<repo>"
  exit 1
fi

if [ -z "${RUNNER_TOKEN:-}" ]; then
  echo "RUNNER_TOKEN not set. Create a registration token in GitHub and set RUNNER_TOKEN environment variable."
  exit 1
fi

RUNNER_VERSION=${RUNNER_VERSION:-2.308.0}
ARCHIVE=actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
URL=https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${ARCHIVE}

mkdir -p actions-runner
cd actions-runner

echo "Downloading runner ${RUNNER_VERSION}..."
curl -fsSLO "$URL"
tar xzf "$ARCHIVE"

echo "Configuring runner..."
./config.sh --url "$GITHUB_URL" --token "$RUNNER_TOKEN" --name "$RUNNER_NAME" --labels "$RUNNER_LABELS" --unattended

echo "Starting runner in foreground (Ctrl-C to stop). To run as a service, see README"
./run.sh
