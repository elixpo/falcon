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


def generate_2026_timestamps(count):
    """Generate timestamps across 2026, weighted toward end of year.

    Uses power distribution (r^0.5) so the contribution graph shows
    activity all year with heavier highlights toward Dec 2026.
    """
    start = datetime(2026, 1, 1)
    total_seconds = 364 * 86400  # seconds in 2026

    timestamps = []
    for _ in range(count):
        # r^0.5 biases toward higher values → more commits late in 2026
        r = random.random() ** 0.5
        offset = int(r * total_seconds)
        ts = start + timedelta(seconds=offset)
        # Randomize time of day for natural look
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
    commits_per_session = config.get("commits_per_session", 200000)
    push_interval = config.get("push_interval", 5000)
    readme_interval = config.get("readme_update_interval", 5000)
    branch = config.get("branch", "main")

    # Apply git performance optimizations
    setup_git_optimizations()

    current = get_current_count()

    if current >= target:
        print(f"[falcon] Target reached! {current:,}/{target:,}")
        return

    remaining = target - current
    num_commits = min(commits_per_session, remaining)

    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

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

    print(f"[falcon] Session: {num_commits:,} commits")
    print(f"[falcon] Current: {current:,} / Target: {target:,}")
    print(f"[falcon] Using git plumbing for maximum speed")

    # Generate 2026 timestamps for contribution graph
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
            # Must update-ref first so stage_files works against current HEAD
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
