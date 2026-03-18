#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_DIR="$SCRIPT_DIR/systemd"

echo "╔══════════════════════════════════════════╗"
echo "║     FALCON SYSTEMD INSTALLER             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Copy unit files
echo "[1/4] Copying unit files to /etc/systemd/system/ ..."
sudo cp "$SERVICE_DIR/falcon.service" /etc/systemd/system/falcon.service
sudo cp "$SERVICE_DIR/falcon.timer" /etc/systemd/system/falcon.timer

# Reload systemd
echo "[2/4] Reloading systemd daemon ..."
sudo systemctl daemon-reload

# Enable and start the timer
echo "[3/4] Enabling falcon.timer ..."
sudo systemctl enable falcon.timer

echo "[4/4] Starting falcon.timer ..."
sudo systemctl start falcon.timer

echo ""
echo "✓ Falcon systemd timer installed and running!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status falcon.timer    # Check timer status"
echo "  sudo systemctl list-timers falcon*    # See next scheduled run"
echo "  sudo systemctl start falcon.service   # Run manually now"
echo "  journalctl -u falcon.service -f       # Watch logs"
echo "  sudo systemctl stop falcon.timer      # Stop the timer"
echo "  sudo systemctl disable falcon.timer   # Disable permanently"
