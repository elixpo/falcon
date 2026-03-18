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
    weights = [a.get("weight", 1) for a in co_authors]
    author = random.choices(co_authors, weights=weights, k=1)[0]
    return f"Co-authored-by: {author['name']} <{author['email']}>"


def make_commit(count, target, session, co_authors, committer=None):
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

    # Commit as lixiorg (committer), co-authors get attributed in trailer
    env = os.environ.copy()
    if committer:
        env["GIT_AUTHOR_NAME"] = committer["name"]
        env["GIT_AUTHOR_EMAIL"] = committer["email"]
        env["GIT_COMMITTER_NAME"] = committer["name"]
        env["GIT_COMMITTER_EMAIL"] = committer["email"]

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=ROOT_DIR, capture_output=True, check=True, env=env
    )


def push(branch="main"):
    subprocess.run(
        ["git", "push", "origin", branch],
        cwd=ROOT_DIR, capture_output=True, check=True
    )
