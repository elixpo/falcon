<div align="center">

```
  ███████╗ █████╗ ██╗      ██████╗ ██████╗ ███╗   ██╗
  ██╔════╝██╔══██╗██║     ██╔════╝██╔═══██╗████╗  ██║
  █████╗  ███████║██║     ██║     ██║   ██║██╔██╗ ██║
  ██╔══╝  ██╔══██║██║     ██║     ██║   ██║██║╚██╗██║
  ██║     ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
  ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
```

### High-Altitude Commit Engine

**Tracking progress to 200,000 commits with ASCII art precision.**

[![Commits](https://img.shields.io/github/commit-activity/w/elixpo/falcon?style=for-the-badge&color=00d4ff&label=Weekly%20Commits)](https://github.com/elixpo/falcon/commits/main)
[![Total Commits](https://img.shields.io/github/last-commit/elixpo/falcon?style=for-the-badge&color=7c3aed&label=Last%20Commit)](https://github.com/elixpo/falcon)
[![CI](https://img.shields.io/github/actions/workflow/status/elixpo/falcon/falcon-ci.yml?style=for-the-badge&color=22c55e&label=CI)](https://github.com/elixpo/falcon/actions)
[![Stars](https://img.shields.io/github/stars/elixpo/falcon?style=for-the-badge&color=fbbf24)](https://github.com/elixpo/falcon)

</div>

---

## What is Falcon?

Falcon is a commit progress tracker that visualizes milestones using ASCII art. Every commit updates a real-time counter rendered in large block characters — a living scoreboard inside the repo itself.

```
  Current progress:

  ┌─────────────────────────────────────────┐
  │                                         │
  │   ██████╗  ██████╗  ██████╗             │
  │   ╚════██╗██╔═████╗██╔═████╗            │
  │    █████╔╝██║██╔██║██║██╔██║            │
  │    ╚═══██╗████╔╝██║████╔╝██║            │
  │   ██████╔╝╚██████╔╝╚██████╔╝           │
  │   ╚═════╝  ╚═════╝  ╚═════╝            │
  │                                         │
  └─────────────────────────────────────────┘

  █████████████░░░░░░░░░░░░░░░░░░░░  15.00%
```

## How It Works

Falcon runs on a schedule — 7 sessions per week, each producing **900–1,000 commits**. Every commit updates `progress.txt` with:

- The current commit count rendered as large ASCII digits
- A progress bar showing % toward the 200k target
- Timestamp and session metadata

Multiple contributors are credited across commits to reflect the collaborative nature of the project.

## Project Structure

```
falcon/
├── falcon/                  # Core Python package
│   ├── __init__.py
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
│   ├── falcon.service
│   └── falcon.timer
├── .github/workflows/       # CI pipeline
│   └── falcon-ci.yml
├── config.json              # Settings: commit range, co-authors, target
├── progress.txt             # Live progress tracker (auto-updated)
└── README.md
```

## Setup

```bash
# Clone and enter
git clone https://github.com/elixpo/falcon.git
cd falcon

# Run manually
python3 -m falcon

# Set up cron jobs (7 random times across the week)
python3 scripts/setup_cron.py --dry-run
python3 scripts/setup_cron.py

# Or use systemd (recommended for always-on machines)
sudo ./scripts/setup_systemd.sh
```

## Configuration

Edit `config.json` to adjust:

```json
{
  "min_commits_per_day": 900,
  "max_commits_per_day": 1000,
  "target_commits": 200000,
  "auto_push": true,
  "co_authors": [...]
}
```

## The Target

<div align="center">

| Metric | Value |
|--------|-------|
| **Target** | 200,000 commits |
| **Daily Rate** | 900 – 1,000 |
| **Sessions/Week** | 7 |
| **ETA** | ~200 days |

</div>

## Contributors

Built and maintained by the Falcon team. Each commit is a step forward.

---

<div align="center">

*Falcon doesn't rest. Falcon commits.*

</div>
