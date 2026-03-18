import math
from datetime import datetime

from .ascii_art import BANNER, render_ascii_number


def make_progress_bar(current, target, width=40):
    pct = min(current / target, 1.0)
    filled = int(width * pct)
    empty = width - filled
    bar = "\u2588" * filled + "\u2591" * empty
    return f"  {bar}  {pct * 100:.2f}%"


def make_progress_bar_md(current, target, width=30):
    pct = min(current / target, 1.0)
    filled = int(width * pct)
    empty = width - filled
    bar = "\u2588" * filled + "\u2591" * empty
    return f"`{bar}` **{pct * 100:.2f}%**"


def generate_progress_content(count, target, session_commits):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ascii_num = render_ascii_number(count)

    return f"""
{BANNER}

  ════════════════════════════════════════════════════
  PROGRESS TRACKER
  ════════════════════════════════════════════════════

  Current Count: {count:,}
  Target: {target:,}

{make_progress_bar(count, target)}

  ┌─────────────────────────────────────────┐
  │                                         │
{ascii_num}
  │                                         │
  └─────────────────────────────────────────┘

  Last updated: {now}
  Session commits: {session_commits:,}
"""


def generate_readme(count, target, co_authors):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pct = min(count / target, 1.0) * 100
    remaining = max(target - count, 0)
    daily_rate = 950  # average
    eta_days = math.ceil(remaining / daily_rate) if remaining > 0 else 0

    # Build contributor avatars
    author_badges = ""
    for author in co_authors:
        name = author["name"]
        author_badges += f'<a href="https://github.com/{name}"><img src="https://github.com/{name}.png" width="50" style="border-radius:50%"></a>\n'

    progress_bar = make_progress_bar_md(count, target)

    return f"""<div align="center">

```
  ███████╗ █████╗ ██╗      ██████╗ ██████╗ ███╗   ██╗
  ██╔════╝██╔══██╗██║     ██╔════╝██╔═══██╗████╗  ██║
  █████╗  ███████║██║     ██║     ██║   ██║██╔██╗ ██║
  ██╔══╝  ██╔══██║██║     ██║     ██║   ██║██║╚██╗██║
  ██║     ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
  ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
```

**High-Altitude Commit Engine**

[![Commits](https://img.shields.io/github/commit-activity/w/elixpo/falcon?style=for-the-badge&color=00d4ff&label=Weekly%20Commits)](https://github.com/elixpo/falcon/commits/main)
[![Last Commit](https://img.shields.io/github/last-commit/elixpo/falcon?style=for-the-badge&color=7c3aed)](https://github.com/elixpo/falcon)
[![CI](https://img.shields.io/github/actions/workflow/status/elixpo/falcon/falcon-ci.yml?style=for-the-badge&color=22c55e&label=CI)](https://github.com/elixpo/falcon/actions)
[![Stars](https://img.shields.io/github/stars/elixpo/falcon?style=for-the-badge&color=fbbf24)](https://github.com/elixpo/falcon)
[![Contributors](https://img.shields.io/github/contributors/elixpo/falcon?style=for-the-badge&color=f97316)](https://github.com/elixpo/falcon/graphs/contributors)
[![Repo Size](https://img.shields.io/github/repo-size/elixpo/falcon?style=for-the-badge&color=06b6d4)](https://github.com/elixpo/falcon)

</div>

---

## Live Progress

<div align="center">

### {count:,} / {target:,}

{progress_bar}

| Metric | Value |
|:------:|:-----:|
| **Current** | {count:,} |
| **Target** | {target:,} |
| **Remaining** | {remaining:,} |
| **Completion** | {pct:.2f}% |
| **Daily Rate** | ~900 - 1,000 |
| **ETA** | ~{eta_days} days |
| **Last Updated** | {now} |

</div>

---

## What is Falcon?

Falcon is a commit progress tracker that visualizes milestones using ASCII art. Every commit updates a real-time counter rendered in large block characters — a living scoreboard inside the repo itself.

Each session produces **900–1,000 commits**, with every single one updating the progress counter. Multiple contributors are credited across commits to reflect the collaborative nature of the project.

## Architecture

```
falcon/
├── falcon/                  # Core Python package
│   ├── __main__.py          # Entry point (python -m falcon)
│   ├── ascii_art.py         # ASCII digit font + renderer
│   ├── config.py            # Config & state management
│   ├── engine.py            # Session orchestrator
│   ├── git.py               # Git operations (commit, push)
│   └── renderer.py          # Progress bar + content generation
├── scripts/
│   ├── setup_cron.py        # Cron scheduler
│   └── setup_systemd.sh     # Systemd installer
├── systemd/                 # Systemd unit files
├── .github/workflows/       # CI pipeline
├── config.json              # Runtime configuration
└── progress.txt             # Live ASCII art tracker
```

## Quick Start

```bash
git clone https://github.com/elixpo/falcon.git
cd falcon
python3 -m falcon
```

## Contributors

<div align="center">

{author_badges}
<a href="https://github.com/Circuit-Overtime"><img src="https://github.com/Circuit-Overtime.png" width="50" style="border-radius:50%"></a>

</div>

---

<div align="center">

*Falcon doesn't rest. Falcon commits.*

**{count:,}** commits and counting.

</div>
"""
