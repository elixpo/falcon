#!/usr/bin/env python3
"""
Generate and install cron jobs for Falcon.
Creates 7 entries — one for each day of the week at a random time.
"""

import random
import subprocess
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, "falcon.log")
PYTHON = os.path.join(ROOT_DIR, "venv", "bin", "python3")

if not os.path.exists(PYTHON):
    PYTHON = sys.executable


def generate_cron_entries():
    entries = []
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    for day_num in range(7):
        hour = random.randint(6, 22)
        minute = random.randint(0, 59)
        cron_line = f"{minute} {hour} * * {day_num} cd {ROOT_DIR} && {PYTHON} -m falcon >> {LOG_FILE} 2>&1"
        entries.append((days[day_num], hour, minute, cron_line))

    return entries


def install_cron(entries):
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    filtered = [
        line for line in existing.strip().split("\n")
        if line.strip() and "falcon" not in line
    ]

    filtered.append("")
    filtered.append("# === FALCON AUTO-COMMIT ENGINE ===")
    for _, _, _, cron_line in entries:
        filtered.append(cron_line)
    filtered.append("# === END FALCON ===")
    filtered.append("")

    new_crontab = "\n".join(filtered)

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
