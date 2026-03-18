import random
import subprocess
import sys
from datetime import datetime

from .config import load_config, load_state, save_state
from .git import get_current_count, make_commit, push


def run_session():
    config = load_config()
    target = config["target_commits"]
    co_authors = config["co_authors"]
    committer = config.get("committer")
    min_c = config["min_commits_per_day"]
    max_c = config["max_commits_per_day"]
    state = load_state()

    current = get_current_count()

    if current >= target:
        print(f"[falcon] Target reached! {current:,}/{target:,}")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    # Resume interrupted session if one exists for today
    pending = state.get("pending_session")
    if pending and pending["date"] == today:
        num_commits = pending["remaining"]
        print(f"[falcon] Resuming interrupted session: {num_commits:,} commits left")
    else:
        num_commits = random.randint(min_c, max_c)
        remaining = target - current
        num_commits = min(num_commits, remaining)

    # Save pending state before starting
    state["pending_session"] = {
        "date": today,
        "planned": num_commits,
        "remaining": num_commits,
    }
    save_state(state)

    print(f"[falcon] Starting session: {num_commits:,} commits")
    print(f"[falcon] Current: {current:,} | Target: {target:,}")

    completed = 0
    for i in range(num_commits):
        try:
            make_commit(current + i, target, i, co_authors, committer)
            completed += 1

            if (i + 1) % 100 == 0:
                print(f"[falcon] ... {i + 1}/{num_commits} commits done")

            # Push every 50 commits
            if (i + 1) % 50 == 0 and config.get("auto_push", True):
                try:
                    push(config.get("branch", "main"))
                    print(f"[falcon] Pushed batch at commit {i + 1}")
                except subprocess.CalledProcessError as e:
                    print(f"[falcon] Batch push failed: {e}", file=sys.stderr)

            # Checkpoint state every 10 commits
            if (i + 1) % 10 == 0:
                state["pending_session"]["remaining"] = num_commits - completed
                save_state(state)

        except subprocess.CalledProcessError as e:
            print(f"[falcon] Commit failed at {i + 1}: {e}", file=sys.stderr)
            state["pending_session"]["remaining"] = num_commits - completed
            save_state(state)
            break

    # Final push for remainder
    if config.get("auto_push", True) and completed % 50 != 0:
        try:
            push(config.get("branch", "main"))
            print(f"[falcon] Final push complete ({completed:,} commits)")
        except subprocess.CalledProcessError as e:
            print(f"[falcon] Push failed: {e}", file=sys.stderr)

    # Mark session complete
    final_count = get_current_count()
    state["total_sessions"] += 1
    state["total_commits_made"] += completed
    state["last_session_date"] = today
    state["pending_session"] = None
    save_state(state)

    print(f"[falcon] Session complete. Total: {final_count:,}")
