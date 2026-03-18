#!/usr/bin/env python3
"""
Generate and install cron jobs for Falcon.
Creates 7 entries — one for each day of the week at a random time.
"""

import random
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FALCON_SCRIPT = os.path.join(SCRIPT_DIR, "falcon.py")
LOG_FILE = os.path.join(SCRIPT_DIR, "falcon.log")
PYTHON = os.path.join(SCRIPT_DIR, "venv", "bin", "python3")

# Fallback to system python if venv doesn't exist
if not os.path.exists(PYTHON):
    PYTHON = sys.executable


def generate_cron_entries():
    """Generate 7 cron entries with random times, one per day of the week."""
    entries = []
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    for day_num in range(7):
        hour = random.randint(6, 22)      # Between 6 AM and 10 PM
        minute = random.randint(0, 59)
        # day_of_week: 0 = Sunday, 6 = Saturday
        cron_line = f"{minute} {hour} * * {day_num} cd {SCRIPT_DIR} && {PYTHON} {FALCON_SCRIPT} >> {LOG_FILE} 2>&1"
        entries.append((days[day_num], hour, minute, cron_line))

    return entries


def install_cron(entries):
    """Install cron entries, preserving existing non-falcon crons."""
    # Get existing crontab
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # Filter out old falcon entries
    filtered = [
        line for line in existing.strip().split("\n")
        if line.strip() and "falcon.py" not in line
    ]

    # Add header and new entries
    filtered.append("")
    filtered.append("# === FALCON AUTO-COMMIT ENGINE ===")
    for _, _, _, cron_line in entries:
        filtered.append(cron_line)
    filtered.append("# === END FALCON ===")
    filtered.append("")

    new_crontab = "\n".join(filtered)

    # Install
    proc = subprocess.run(
        ["crontab", "-"], input=new_crontab, text=True,
        capture_output=True
    )
    return proc.returncode == 0


def main():
    print("╔══════════════════════════════════════════╗")
    print("║     FALCON CRON SCHEDULER SETUP          ║")
    print("╚══════════════════════════════════════════╝")
    print()

    entries = generate_cron_entries()

    print("Generated schedule:")
    print("─" * 45)
    for day, hour, minute, _ in entries:
        print(f"  {day}  →  {hour:02d}:{minute:02d}")
    print("─" * 45)
    print()

    if "--dry-run" in sys.argv:
        print("[dry-run] Cron entries NOT installed.")
        print()
        for _, _, _, line in entries:
            print(f"  {line}")
        return

    if install_cron(entries):
        print("✓ Cron jobs installed successfully!")
        print(f"  Logs: {LOG_FILE}")
    else:
        print("✗ Failed to install cron jobs.", file=sys.stderr)
        sys.exit(1)

    print()
    print("Verify with: crontab -l")


if __name__ == "__main__":
    main()
