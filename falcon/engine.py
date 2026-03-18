import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta

from .config import load_config, load_state, save_state, ROOT_DIR, PROGRESS_FILE
from .git import (
    get_current_count, get_head_commit, write_tree, stage_files,
    commit_tree, update_ref, push, setup_git_optimizations, gc_cleanup,
    README_FILE,
)
from .renderer import generate_readme


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

    Bright dates (forming '2026') get 8x more commits than background.
    All days get some commits so every square is filled.
    """
    bright = build_2026_pattern()

    start = datetime(2026, 1, 1).date()
    all_days = [start + timedelta(days=i) for i in range(365)]

    # Weight: bright=50, background=1
    # High ratio ensures bg days land in Q1 (dark green) and
    # bright days land in Q4 (neon green) for maximum contrast
    BRIGHT_WEIGHT = 50
    BG_WEIGHT = 1
    weights = []
    for day in all_days:
        weights.append(BRIGHT_WEIGHT if day in bright else BG_WEIGHT)

    total_weight = sum(weights)

    # Distribute commits proportionally
    # Only enforce min 1/day (fill all squares) when count >= 365
    min_per_day = 1 if count >= 365 else 0
    day_commits = {}
    assigned = 0
    for day, w in zip(all_days, weights):
        n = max(min_per_day, int(count * w / total_weight))
        day_commits[day] = n
        assigned += n

    # Fix remainder — distribute across all days until exact
    diff = count - assigned
    while diff > 0:
        pool = list(bright) if diff > len(all_days) else all_days
        batch = min(diff, len(pool))
        for day in random.sample(pool, batch):
            day_commits[day] += 1
        diff -= batch
    while diff < 0:
        bg_days = [d for d in all_days if d not in bright and day_commits[d] > 1]
        if not bg_days:
            break
        batch = min(-diff, len(bg_days))
        for day in random.sample(bg_days, batch):
            day_commits[day] -= 1
        diff += batch

    # Generate actual timestamps
    timestamps = []
    for day, n in day_commits.items():
        for _ in range(n):
            ts = datetime.combine(day, datetime.min.time())
            ts = ts.replace(
                hour=random.randint(8, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )
            timestamps.append(ts)

    timestamps.sort()
    return timestamps


def run_session():
    config = load_config()
    target = config["target_commits"]
    committer = config["committer"]
    daily_target = config.get("daily_target", 200000)
    push_interval = config.get("push_interval", 5000)
    readme_interval = config.get("readme_update_interval", 5000)
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

    # Get initial state
    parent = get_head_commit()

    # Write initial README and get tree
    readme = generate_readme(current, target)
    with open(README_FILE, "w") as f:
        f.write(readme)
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(current))
    stage_files("README.md", "progress.txt")
    tree = write_tree()

    start_time = time.time()
    completed = 0

    for i in range(num_commits):
        count = current + i + 1
        ts = timestamps[i]
        date_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str

        # Update files and tree periodically
        if i > 0 and i % readme_interval == 0:
            update_ref(branch, parent)
            readme = generate_readme(count, target)
            with open(README_FILE, "w") as f:
                f.write(readme)
            with open(PROGRESS_FILE, "w") as f:
                f.write(str(count))
            stage_files("README.md", "progress.txt")
            tree = write_tree()

        # Create commit using plumbing (no hooks, no index scan)
        try:
            parent = commit_tree(tree, parent, f"falcon: {count:,}/{target:,}", env)
            completed += 1
        except subprocess.CalledProcessError as e:
            print(f"[falcon] commit-tree failed at {i + 1}: {e}", file=sys.stderr)
            update_ref(branch, parent)
            state["pending_session"]["remaining"] = num_commits - completed
            save_state(state)
            break

        # Push periodically
        if completed % push_interval == 0 and config.get("auto_push", True):
            update_ref(branch, parent)
            try:
                push(branch)
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"[falcon] Pushed {completed:,}/{num_commits:,} | {rate:.0f} commits/sec")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"[falcon] Push failed at {completed:,}: {e}", file=sys.stderr)

        # Checkpoint state every 50k commits
        if completed % 50000 == 0:
            state["pending_session"]["remaining"] = num_commits - completed
            save_state(state)

    # Final: update files, ref, and push
    final_count = current + completed
    update_ref(branch, parent)

    readme = generate_readme(final_count, target)
    with open(README_FILE, "w") as f:
        f.write(readme)
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(final_count))
    stage_files("README.md", "progress.txt")

    # Final commit with current timestamp
    now = datetime.now()
    env["GIT_AUTHOR_DATE"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"]
    tree = write_tree()
    final_commit = commit_tree(tree, parent, f"falcon: {final_count:,}/{target:,}", env)
    update_ref(branch, final_commit)

    if config.get("auto_push", True):
        try:
            push(branch)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("[falcon] Final push failed", file=sys.stderr)

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
