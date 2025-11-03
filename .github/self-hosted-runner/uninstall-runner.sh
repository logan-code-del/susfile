#!/usr/bin/env bash
set -euo pipefail

# Unregister and cleanup a previously installed runner
RUNNER_DIR=$(pwd)/actions-runner

if [ ! -d "$RUNNER_DIR" ]; then
  echo "Runner directory not found at $RUNNER_DIR"
  exit 1
fi

cd "$RUNNER_DIR"
echo "Stopping runner (if running)"
./svc.sh stop || true

echo "Removing runner registration (you will need a removal token if required)"
./config.sh remove --unattended || true

echo "Cleaning up files"
cd ..
rm -rf "$RUNNER_DIR"

echo "Runner removed. Please also remove any systemd unit if created."
