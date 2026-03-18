import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta

from .config import load_config, load_state, save_state, ROOT_DIR, PROGRESS_FILE
from .git import (
    get_current_count, get_head_commit, write_tree,
    commit_tree, update_ref, push, setup_git_optimizations, gc_cleanup,
)


# 5×7 pixel font for contribution graph (row=day_of_week, col=week)
GRAPH_DIGITS = {
    "2": [
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
    ],
    "0": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    "6": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
}


def build_2026_pattern():
    """Build set of dates that spell '2026' on GitHub's contribution graph.

    GitHub graph: 7 rows (Sun=0..Sat=6), ~53 columns (weeks).
    Jan 1, 2026 = Thursday. Base Sunday = Dec 28, 2025.
    """
    base = datetime(2025, 12, 28)  # Sunday before Jan 1, 2026

    # "2","0","2","6" — each 5 cols wide, 1 col gap, total 23 cols
    # Centered in ~53 cols: start at col 15
    text = "2026"
    digit_positions = []
    col = 15
    for ch in text:
        digit_positions.append((ch, col))
        col += 6  # 5 wide + 1 gap

    bright_dates = set()
    for ch, start_col in digit_positions:
        pattern = GRAPH_DIGITS[ch]
        for row in range(7):
            for dcol in range(5):
                if pattern[row][dcol]:
                    week_col = start_col + dcol
                    date = base + timedelta(days=week_col * 7 + row)
                    if date.year == 2026:
                        bright_dates.add(date.date())

    return bright_dates


def generate_2026_timestamps(count):
    """Generate timestamps that paint '2026' on the contribution graph.

    '2026' days get the bulk of commits (brightest green).
    All other days get 1 commit each (lowest green, not blank).
    Returns a sorted list of ISO date strings (not datetime objects).
    """
    bright = build_2026_pattern()

    start = datetime(2026, 1, 1).date()
    all_days = [start + timedelta(days=i) for i in range(365)]
    bg_days = [d for d in all_days if d not in bright]

    # Background days get exactly 1 commit each (lowest green)
    bg_total = len(bg_days)
    bright_total = max(0, count - bg_total)

    bright_list = sorted(bright)
    per_bright = bright_total // len(bright_list) if bright_list else 0
    bright_remainder = bright_total % len(bright_list) if bright_list else 0

    # Build flat list of (day, n_commits) pairs
    day_counts = []
    for day in bg_days:
        day_counts.append((day, 1))
    for i, day in enumerate(bright_list):
        day_counts.append((day, per_bright + (1 if i < bright_remainder else 0)))

    # Generate all timestamp strings in batch using pre-computed random values
    timestamps = []
    for day, n in day_counts:
        base = f"{day.year}-{day.month:02d}-{day.day:02d}T"
        for _ in range(n):
            timestamps.append(f"{base}{random.randint(8,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}")

    timestamps.sort()
    return timestamps


def run_session():
    config = load_config()
    target = config["target_commits"]
    committer = config["committer"]
    daily_target = config.get("daily_target", 200000)
    branch = config.get("branch", "main")

    # Apply git performance optimizations
    setup_git_optimizations()

    current = get_current_count()

    if current >= target:
        print(f"[falcon] Target reached! {current:,}/{target:,}")
        return

    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if today's daily target was already hit
    if state.get("last_session_date") == today and not state.get("pending_session"):
        print(f"[falcon] Daily target already hit for {today}. Skipping.")
        return

    remaining = target - current
    num_commits = min(daily_target, remaining)

    # Resume interrupted session
    pending = state.get("pending_session")
    if pending and pending["date"] == today:
        num_commits = pending["remaining"]
        print(f"[falcon] Resuming: {num_commits:,} commits left")

    state["pending_session"] = {
        "date": today,
        "planned": num_commits,
        "remaining": num_commits,
    }
    save_state(state)

    bright_count = len(build_2026_pattern())
    print(f"[falcon] Session: {num_commits:,} commits")
    print(f"[falcon] Current: {current:,} / Target: {target:,}")
    print(f"[falcon] Pattern: '2026' on contribution graph ({bright_count} bright days)")
    print(f"[falcon] Using git plumbing for maximum speed")

    # Generate timestamps that paint "2026" on the contribution graph
    timestamps = generate_2026_timestamps(num_commits)

    # Prepare committer environment
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = committer["name"]
    env["GIT_AUTHOR_EMAIL"] = committer["email"]
    env["GIT_COMMITTER_NAME"] = committer["name"]
    env["GIT_COMMITTER_EMAIL"] = committer["email"]

    # Get current HEAD tree and commit — all empty commits reuse this tree
    parent = get_head_commit()
    tree = write_tree()

    start_time = time.time()
    completed = 0

    # ── All commits are empty (same tree as parent, no file I/O) ──
    for i in range(num_commits):
        count = current + i + 1
        env["GIT_AUTHOR_DATE"] = timestamps[i]
        env["GIT_COMMITTER_DATE"] = timestamps[i]

        try:
            parent = commit_tree(tree, parent, f"falcon: {count:,}/{target:,}", env)
            completed += 1
        except subprocess.CalledProcessError as e:
            print(f"[falcon] commit-tree failed at {i + 1}: {e}", file=sys.stderr)
            update_ref(branch, parent)
            state["pending_session"]["remaining"] = num_commits - completed
            save_state(state)
            break

        # Progress log every 10k commits
        if completed % 10000 == 0:
            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            print(f"[falcon] Progress {completed:,}/{num_commits:,} | {rate:.0f} commits/sec")

        # Checkpoint state every 50k commits (crash recovery)
        if completed % 50000 == 0:
            update_ref(branch, parent)
            state["pending_session"]["remaining"] = num_commits - completed
            save_state(state)

    # ── Finalize: update ref and push ──
    final_count = current + completed
    update_ref(branch, parent)

    # Save progress counter locally (README is updated by CI)
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(final_count))

    # ── Single push for the entire session ──
    if config.get("auto_push", True):
        print(f"[falcon] Pushing {completed:,} commits...")
        try:
            push(branch)
            print(f"[falcon] Push complete")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"[falcon] Push failed: {e}", file=sys.stderr)
            print(f"[falcon] Commits are saved locally — retry with: git push origin {branch}")

    elapsed = time.time() - start_time
    rate = completed / elapsed if elapsed > 0 else 0

    # Update state
    state["total_sessions"] += 1
    state["total_commits_made"] += completed
    state["last_session_date"] = today
    state["pending_session"] = None
    save_state(state)

    print(f"[falcon] Done. {completed:,} commits in {elapsed:.0f}s ({rate:.0f} commits/sec)")
    print(f"[falcon] Total: {final_count:,}/{target:,}")

    # Compress repo after session
    print("[falcon] Running git gc...")
    gc_cleanup()
    print("[falcon] gc complete")
