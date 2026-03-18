import os
import subprocess

from .config import ROOT_DIR, PROGRESS_FILE

README_FILE = os.path.join(ROOT_DIR, "README.md")


def setup_git_optimizations():
    """Apply all git performance tweaks for maximum commit speed."""
    opts = {
        "gc.auto": "0",
        "core.preloadIndex": "true",
        "core.fscache": "true",
        "pack.threads": "0",
        "commit.gpgsign": "false",
        "core.hooksPath": "/dev/null",
        "core.autocrlf": "false",
        "core.fsmonitor": "false",
        "core.untrackedCache": "false",
        "receive.autogc": "false",
        "gc.autoDetach": "false",
    }
    for key, val in opts.items():
        subprocess.run(
            ["git", "config", key, val],
            cwd=ROOT_DIR, capture_output=True
        )


def get_current_count():
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=ROOT_DIR, capture_output=True, text=True
    )
    return int(result.stdout.strip())


def get_head_commit():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT_DIR, capture_output=True, text=True
    )
    return result.stdout.strip()


def write_tree():
    """Write current index to a tree object and return its hash."""
    result = subprocess.run(
        ["git", "write-tree"],
        cwd=ROOT_DIR, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def stage_files(*files):
    subprocess.run(
        ["git", "add"] + list(files),
        cwd=ROOT_DIR, capture_output=True, check=True
    )


def commit_tree(tree, parent, message, env):
    """Create a commit object using git plumbing. Returns commit hash."""
    result = subprocess.run(
        ["git", "commit-tree", tree, "-p", parent, "-m", message],
        cwd=ROOT_DIR, capture_output=True, text=True, check=True, env=env
    )
    return result.stdout.strip()


def update_ref(branch, commit_hash):
    subprocess.run(
        ["git", "update-ref", f"refs/heads/{branch}", commit_hash],
        cwd=ROOT_DIR, capture_output=True, check=True
    )


def push(branch="main", retries=3):
    """Push to remote with retries. Timeout 10 min per attempt."""
    for attempt in range(1, retries + 1):
        try:
            subprocess.run(
                ["git", "push", "origin", branch],
                cwd=ROOT_DIR, capture_output=True, check=True, timeout=600
            )
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            if attempt < retries:
                import time
                wait = attempt * 30
                print(f"[falcon] Push attempt {attempt}/{retries} failed, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def gc_cleanup():
    """Run aggressive gc after session to compress objects."""
    subprocess.run(
        ["git", "gc", "--aggressive", "--prune=now"],
        cwd=ROOT_DIR, capture_output=True, timeout=600
    )
