#!/usr/bin/env python3
"""
Falcon — Automated commit engine with ASCII art progress tracking.
All commits are made from the repo owner's git config.
Co-authors are added as commit trailers for natural appearance.
"""

import json
import os
import random
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
PROGRESS_FILE = os.path.join(SCRIPT_DIR, "progress.txt")

# ASCII digit font (5 lines tall)
DIGITS = {
    "0": [
        " ██████╗ ",
        "██╔═████╗",
        "██║██╔██║",
        "████╔╝██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ],
    "1": [
        " ██╗",
        "███║",
        "╚██║",
        " ██║",
        " ██║",
        " ╚═╝",
    ],
    "2": [
        "██████╗ ",
        "╚════██╗",
        " █████╔╝",
        "██╔═══╝ ",
        "███████╗",
        "╚══════╝",
    ],
    "3": [
        "██████╗ ",
        "╚════██╗",
        " █████╔╝",
        " ╚═══██╗",
        "██████╔╝",
        "╚═════╝ ",
    ],
    "4": [
        "██╗  ██╗",
        "██║  ██║",
        "███████║",
        "╚════██║",
        "     ██║",
        "     ╚═╝",
    ],
    "5": [
        "███████╗",
        "██╔════╝",
        "███████╗",
        "╚════██║",
        "███████║",
        "╚══════╝",
    ],
    "6": [
        " ██████╗",
        "██╔════╝",
        "██████╗ ",
        "██╔══██╗",
        "╚█████╔╝",
        " ╚════╝ ",
    ],
    "7": [
        "███████╗",
        "╚════██║",
        "    ██╔╝",
        "   ██╔╝ ",
        "   ██║  ",
        "   ╚═╝  ",
    ],
    "8": [
        " █████╗ ",
        "██╔══██╗",
        "╚█████╔╝",
        "██╔══██╗",
        "╚█████╔╝",
        " ╚════╝ ",
    ],
    "9": [
        " █████╗ ",
        "██╔══██╗",
        "╚██████║",
        " ╚═══██║",
        " █████╔╝",
        " ╚════╝ ",
    ],
    ",": [
        "   ",
        "   ",
        "   ",
        "   ",
        "▐█╗",
        "╚═╝",
    ],
}


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_current_count():
    """Count total commits in the repo."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=SCRIPT_DIR, capture_output=True, text=True
    )
    return int(result.stdout.strip())


def format_number(n):
    """Format number with commas: 1234567 -> 1,234,567"""
    return f"{n:,}"


def render_ascii_number(n):
    """Render a number as big ASCII art."""
    formatted = format_number(n)
    lines = [""] * 6
    for ch in formatted:
        if ch in DIGITS:
            for i in range(6):
                lines[i] += DIGITS[ch][i] + " "
    return "\n".join("  " + line for line in lines)


def make_progress_bar(current, target, width=40):
    """Create a progress bar."""
    pct = min(current / target, 1.0)
    filled = int(width * pct)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"  {bar}  {pct * 100:.2f}%"


def generate_progress_content(count, target, session_commits):
    """Generate the full progress.txt content."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ascii_num = render_ascii_number(count)

    return f"""
  ███████╗ █████╗ ██╗      ██████╗ ██████╗ ███╗   ██╗
  ██╔════╝██╔══██╗██║     ██╔════╝██╔═══██╗████╗  ██║
  █████╗  ███████║██║     ██║     ██║   ██║██╔██╗ ██║
  ██╔══╝  ██╔══██║██║     ██║     ██║   ██║██║╚██╗██║
  ██║     ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
  ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

  ════════════════════════════════════════════════════
  PROGRESS TRACKER
  ════════════════════════════════════════════════════

  Current Count: {format_number(count)}
  Target: {format_number(target)}

{make_progress_bar(count, target)}

  ┌─────────────────────────────────────────┐
  │                                         │
{ascii_num}
  │                                         │
  └─────────────────────────────────────────┘

  Last updated: {now}
  Session commits: {format_number(session_commits)}
"""


def pick_co_author(co_authors):
    """Pick a random co-author for the commit trailer."""
    author = random.choice(co_authors)
    return f"Co-authored-by: {author['name']} <{author['email']}>"


def make_commit(count, target, session, co_authors):
    """Write progress file and create a commit."""
    content = generate_progress_content(count + 1, target, session + 1)
    with open(PROGRESS_FILE, "w") as f:
        f.write(content)

    subprocess.run(["git", "add", "progress.txt"], cwd=SCRIPT_DIR, check=True)

    # Build commit message with co-author trailer
    co_author_line = pick_co_author(co_authors)
    commit_msg = f"falcon: progress {format_number(count + 1)}/{format_number(target)}\n\n{co_author_line}"

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=SCRIPT_DIR, capture_output=True, check=True
    )


def push():
    """Push to remote."""
    subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=SCRIPT_DIR, capture_output=True, check=True
    )


def run_session():
    """Run a single commit session."""
    config = load_config()
    target = config["target_commits"]
    co_authors = config["co_authors"]
    min_c = config["min_commits_per_day"]
    max_c = config["max_commits_per_day"]

    current = get_current_count()

    if current >= target:
        print(f"[falcon] Target reached! {format_number(current)}/{format_number(target)}")
        return

    # Determine how many commits this session
    num_commits = random.randint(min_c, max_c)
    remaining = target - current
    num_commits = min(num_commits, remaining)

    print(f"[falcon] Starting session: {format_number(num_commits)} commits")
    print(f"[falcon] Current: {format_number(current)} | Target: {format_number(target)}")

    for i in range(num_commits):
        try:
            make_commit(current + i, target, i, co_authors)
            if (i + 1) % 100 == 0:
                print(f"[falcon] ... {i + 1}/{num_commits} commits done")
        except subprocess.CalledProcessError as e:
            print(f"[falcon] Commit failed at {i + 1}: {e}", file=sys.stderr)
            break

    # Push after all commits
    if config.get("auto_push", True):
        try:
            push()
            print(f"[falcon] Pushed {format_number(num_commits)} commits to origin/main")
        except subprocess.CalledProcessError as e:
            print(f"[falcon] Push failed: {e}", file=sys.stderr)

    final_count = get_current_count()
    print(f"[falcon] Session complete. Total: {format_number(final_count)}")


if __name__ == "__main__":
    run_session()
