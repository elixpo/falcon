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


def _milestone_markers(count, target):
    """Generate milestone checkpoints."""
    milestones = [1000, 5000, 10000, 25000, 50000, 75000, 100000, 150000, 200000]
    lines = ""
    for m in milestones:
        if m > target:
            break
        if count >= m:
            lines += f"| **{m:,}** | :white_check_mark: Reached |\n"
        else:
            lines += f"| **{m:,}** | :hourglass_flowing_sand: Pending |\n"
    return lines


def _activity_graph(count, target):
    """Generate a text-based activity heatmap row."""
    # Show last 7 'days' as intensity blocks based on progress zones
    blocks = ["\u2591", "\u2592", "\u2593", "\u2588"]
    pct = min(count / target, 1.0)
    # Fill proportionally — more blocks light up as we progress
    total_cells = 28  # 4 weeks x 7 days
    filled = int(total_cells * pct)
    row = ""
    for i in range(total_cells):
        if i < filled:
            intensity = min(3, (i * 4) // total_cells + 1)
            row += blocks[intensity]
        else:
            row += blocks[0]
        if (i + 1) % 7 == 0:
            row += " "
    return row.strip()


def generate_readme(count, target, co_authors):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pct = min(count / target, 1.0) * 100
    remaining = max(target - count, 0)
    daily_rate = 950
    eta_days = math.ceil(remaining / daily_rate) if remaining > 0 else 0

    # Build contributor avatars
    author_badges = ""
    for author in co_authors:
        name = author["name"]
        author_badges += f'<a href="https://github.com/{name}"><img src="https://github.com/{name}.png" width="50" style="border-radius:50%"></a>\n'

    progress_bar = make_progress_bar_md(count, target)
    milestones = _milestone_markers(count, target)
    heatmap = _activity_graph(count, target)

    return f"""<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:00d4ff,100:7c3aed&height=220&section=header&text=FALCON&fontSize=80&fontColor=ffffff&fontAlignY=35&desc=High-Altitude%20Commit%20Engine&descSize=18&descAlignY=55&animation=twinkling" width="100%"/>

<br>

[![Commits](https://img.shields.io/github/commit-activity/w/elixpo/falcon?style=for-the-badge&color=00d4ff&label=Weekly%20Commits)](https://github.com/elixpo/falcon/commits/main)
[![Last Commit](https://img.shields.io/github/last-commit/elixpo/falcon?style=for-the-badge&color=7c3aed)](https://github.com/elixpo/falcon)
[![CI](https://img.shields.io/github/actions/workflow/status/elixpo/falcon/falcon-ci.yml?style=for-the-badge&color=22c55e&label=CI)](https://github.com/elixpo/falcon/actions)
[![Stars](https://img.shields.io/github/stars/elixpo/falcon?style=for-the-badge&color=fbbf24)](https://github.com/elixpo/falcon)
[![Contributors](https://img.shields.io/github/contributors/elixpo/falcon?style=for-the-badge&color=f97316)](https://github.com/elixpo/falcon/graphs/contributors)
[![Repo Size](https://img.shields.io/github/repo-size/elixpo/falcon?style=for-the-badge&color=06b6d4)](https://github.com/elixpo/falcon)
[![License](https://img.shields.io/github/license/elixpo/falcon?style=for-the-badge&color=ec4899)](https://github.com/elixpo/falcon)

<br>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=elixpo&repo=falcon&theme=react-dark&hide_border=true&area=true&custom_title=Falcon%20Commit%20Activity" width="95%"/>

</div>

---

<div align="center">

## :rocket: Live Progress

<br>

### `{count:,}` / `{target:,}`

{progress_bar}

<br>

| | Metric | Value | |
|:---:|:------:|:-----:|:---:|
| :chart_with_upwards_trend: | **Current** | **{count:,}** | :zap: |
| :dart: | **Target** | **{target:,}** | :checkered_flag: |
| :hourglass: | **Remaining** | **{remaining:,}** | :clock1: |
| :bar_chart: | **Completion** | **{pct:.2f}%** | :fire: |
| :calendar: | **Daily Rate** | **~900 - 1,000** | :repeat: |
| :stopwatch: | **ETA** | **~{eta_days} days** | :rocket: |
| :arrows_counterclockwise: | **Last Updated** | **{now}** | :satellite: |

</div>

---

<div align="center">

## :world_map: Activity Heatmap

```
  {heatmap}
  W1      W2      W3      W4
```

<img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=lixiorg&theme=github_dark" width="95%"/>

</div>

---

<div align="center">

## :trophy: Milestones

| Checkpoint | Status |
|:----------:|:------:|
{milestones}

</div>

---

## :eagle: What is Falcon?

<table>
<tr>
<td width="60%">

Falcon is a commit progress tracker that visualizes milestones using ASCII art. Every commit updates a real-time counter rendered in large block characters — a living scoreboard inside the repo itself.

Each session produces **900-1,000 commits**, with every single one updating the progress counter. Multiple contributors are credited across commits to reflect the collaborative nature of the project.

**Key Features:**
- :art: ASCII art progress counter updated on every commit
- :busts_in_silhouette: Multi-contributor attribution
- :gear: Automated via systemd timers
- :shield: Stateful — survives reboots and interruptions
- :chart_with_upwards_trend: Live README stats that update with each push

</td>
<td width="40%">

```
  ┌────────────────────────┐
  │                        │
  │   ██████╗  ██╗  ██╗    │
  │   ╚════██╗ ██║ ██╔╝    │
  │    █████╔╝ █████╔╝     │
  │   ██╔═══╝  ██╔═██╗     │
  │   ███████╗ ██║  ██╗    │
  │   ╚══════╝ ╚═╝  ╚═╝    │
  │                        │
  │   ████████████░░░░░░   │
  │          62.50%        │
  └────────────────────────┘
```

</td>
</tr>
</table>

---

<details>
<summary><b>:building_construction: Architecture</b></summary>

<br>

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

</details>

<details>
<summary><b>:zap: Quick Start</b></summary>

<br>

```bash
git clone https://github.com/elixpo/falcon.git
cd falcon
python3 -m falcon
```

**Systemd (recommended for always-on):**
```bash
sudo ./scripts/setup_systemd.sh
```

**Cron:**
```bash
python3 scripts/setup_cron.py --dry-run
python3 scripts/setup_cron.py
```

</details>

---

<div align="center">

## :busts_in_silhouette: Contributors

<a href="https://github.com/elixpo/falcon/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=elixpo/falcon&columns=6" />
</a>

<br><br>

{author_badges}
<a href="https://github.com/Circuit-Overtime"><img src="https://github.com/Circuit-Overtime.png" width="50" style="border-radius:50%"></a>

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7c3aed,50:00d4ff,100:0d1117&height=120&section=footer" width="100%"/>

*Falcon doesn't rest. Falcon commits.*

**{count:,}** commits and counting.

</div>
"""
