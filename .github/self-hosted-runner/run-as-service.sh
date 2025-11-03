#!/usr/bin/env bash
set -euo pipefail

# Helper to install the sample systemd service. Edit variables inside the unit as needed.
SERVICE_NAME=actions.runner
UNIT_PATH=/etc/systemd/system/${SERVICE_NAME}.service
RUNNER_DIR=$(pwd)/actions-runner

if [ ! -d "$RUNNER_DIR" ]; then
  echo "Runner directory not found at $RUNNER_DIR. Run install-runner.sh first."
  exit 1
fi

echo "Copying unit file template to $UNIT_PATH (requires sudo)..."
sudo cp actions.runner.service "$UNIT_PATH"
sudo sed -i "s|%WORKING_DIR%|${RUNNER_DIR}|g" "$UNIT_PATH"

echo "Reloading systemd and enabling service"
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "Service started. Use: sudo journalctl -u ${SERVICE_NAME} -f"
