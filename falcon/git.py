import os
import random
import subprocess

from .config import ROOT_DIR, PROGRESS_FILE
from .renderer import generate_progress_content, generate_readme

README_FILE = os.path.join(ROOT_DIR, "README.md")


def get_current_count():
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=ROOT_DIR, capture_output=True, text=True
    )
    return int(result.stdout.strip())


def pick_co_author(co_authors):
    author = random.choice(co_authors)
    return f"Co-authored-by: {author['name']} <{author['email']}>"


def make_commit(count, target, session, co_authors):
    # Update progress.txt
    content = generate_progress_content(count + 1, target, session + 1)
    with open(PROGRESS_FILE, "w") as f:
        f.write(content)

    # Update README.md
    readme = generate_readme(count + 1, target, co_authors)
    with open(README_FILE, "w") as f:
        f.write(readme)

    subprocess.run(["git", "add", "progress.txt", "README.md"], cwd=ROOT_DIR, check=True)

    co_author_line = pick_co_author(co_authors)
    commit_msg = f"falcon: progress {count + 1:,}/{target:,}\n\n{co_author_line}"

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=ROOT_DIR, capture_output=True, check=True
    )


def push(branch="main"):
    subprocess.run(
        ["git", "push", "origin", branch],
        cwd=ROOT_DIR, capture_output=True, check=True
    )
