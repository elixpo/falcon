#!/usr/bin/env python3


import json
import os
import random
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
PROGRESS_FILE = os.path.join(SCRIPT_DIR, "progress.txt")
STATE_FILE = os.path.join(SCRIPT_DIR, "state.json")

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


def load_state():
    """Load persistent state (survives restarts)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "total_sessions": 0,
        "total_commits_made": 0,
        "last_session_date": None,
        "pending_session": None,
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    # state.json is gitignored, purely local tracking


def get_current_count():
    """Count total commits in the repo."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=SCRIPT_DIR, capture_output=True, text=True
    )
    return int(result.stdout.strip())


def format_number(n):
    return f"{n:,}"


def render_ascii_number(n):
    formatted = format_number(n)
    lines = [""] * 6
    for ch in formatted:
        if ch in DIGITS:
            for i in range(6):
                lines[i] += DIGITS[ch][i] + " "
    return "\n".join("  " + line for line in lines)


def make_progress_bar(current, target, width=40):
    pct = min(current / target, 1.0)
    filled = int(width * pct)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"  {bar}  {pct * 100:.2f}%"


def generate_progress_content(count, target, session_commits):
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
    subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=SCRIPT_DIR, capture_output=True, check=True
    )


def run_session():
    config = load_config()
    target = config["target_commits"]
    co_authors = config["co_authors"]
    min_c = config["min_commits_per_day"]
    max_c = config["max_commits_per_day"]
    state = load_state()

    current = get_current_count()

    if current >= target:
        print(f"[falcon] Target reached! {format_number(current)}/{format_number(target)}")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    # Check if we have an interrupted session to resume
    pending = state.get("pending_session")
    if pending and pending["date"] == today:
        num_commits = pending["remaining"]
        print(f"[falcon] Resuming interrupted session: {format_number(num_commits)} commits left")
    else:
        num_commits = random.randint(min_c, max_c)
        remaining = target - current
        num_commits = min(num_commits, remaining)

    # Save pending session state before starting
    state["pending_session"] = {
        "date": today,
        "planned": num_commits,
        "remaining": num_commits,
    }
    save_state(state)

    print(f"[falcon] Starting session: {format_number(num_commits)} commits")
    print(f"[falcon] Current: {format_number(current)} | Target: {format_number(target)}")

    completed = 0
    for i in range(num_commits):
        try:
            make_commit(current + i, target, i, co_authors)
            completed += 1

            if (i + 1) % 100 == 0:
                print(f"[falcon] ... {i + 1}/{num_commits} commits done")

            # Push every 50 commits
            if (i + 1) % 50 == 0 and config.get("auto_push", True):
                try:
                    push()
                    print(f"[falcon] Pushed batch at commit {i + 1}")
                except subprocess.CalledProcessError as e:
                    print(f"[falcon] Batch push failed: {e}", file=sys.stderr)

            # Update remaining count in state every 10 commits
            if (i + 1) % 10 == 0:
                state["pending_session"]["remaining"] = num_commits - completed
                save_state(state)

        except subprocess.CalledProcessError as e:
            print(f"[falcon] Commit failed at {i + 1}: {e}", file=sys.stderr)
            state["pending_session"]["remaining"] = num_commits - completed
            save_state(state)
            break

    # Final push for any remaining commits not covered by the batch push
    if config.get("auto_push", True) and completed % 50 != 0:
        try:
            push()
            print(f"[falcon] Final push complete ({format_number(completed)} commits)")
        except subprocess.CalledProcessError as e:
            print(f"[falcon] Push failed: {e}", file=sys.stderr)

    # Update state — session complete
    final_count = get_current_count()
    state["total_sessions"] += 1
    state["total_commits_made"] += completed
    state["last_session_date"] = today
    state["pending_session"] = None
    save_state(state)

    print(f"[falcon] Session complete. Total: {format_number(final_count)}")


if __name__ == "__main__":
    run_session()
