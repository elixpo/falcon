import json
import os

ROOT_DIR = os.environ.get("FALCON_REPO_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")
PROGRESS_FILE = os.path.join(ROOT_DIR, "progress.txt")
STATE_FILE = os.path.join(ROOT_DIR, "state.json")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def load_state():
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
