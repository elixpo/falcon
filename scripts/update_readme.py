#!/usr/bin/env python3

import math
import subprocess
import sys
from datetime import datetime, timezone

SMALL_DIGITS = {
    "0": ["┌─┐", "│ │", "└─┘"],
    "1": [" ┐ ", " │ ", " ┘ "],
    "2": ["┌─┐", "┌─┘", "└──"],
    "3": ["──┐", " ─┤", "──┘"],
    "4": ["│ │", "└─┤", "  │"],
    "5": ["┌──", "└─┐", "──┘"],
    "6": ["┌──", "├─┐", "└─┘"],
    "7": ["──┐", "  │", "  │"],
    "8": ["┌─┐", "├─┤", "└─┘"],
    "9": ["┌─┐", "└─┤", "──┘"],
    ",": ["   ", "   ", " , "],
}

TARGET = 2000000
DAILY_RATE = 200000


def render_small_number(n):
    formatted = f"{n:,}"
    lines = ["", "", ""]
    for ch in formatted:
        if ch in SMALL_DIGITS:
            for i in range(3):
                lines[i] += SMALL_DIGITS[ch][i] + " "
    return "\n".join(lines)


def progress_bar(pct, width=20):
    filled = int(width * pct / 100)
    return "█" * filled + "░" * (width - filled)


def milestone(count):
    for threshold, label in [
        (1000000, "🏔️ ONE MILLION"),
        (750000, "🔥 750K"),
        (500000, "⚡ HALF MILLION"),
        (250000, "🚀 250K"),
        (100000, "✈️ 100K"),
        (50000, "🛫 50K"),
        (10000, "🦅 10K"),
    ]:
        if count >= threshold:
            return label
    return "🥚 WARMING UP"


def get_commit_count():
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        capture_output=True, text=True
    )
    return int(result.stdout.strip())


def generate_readme(count):
    target = TARGET
    pct = min(count / target, 1.0) * 100 if target > 0 else 0
    remaining = max(target - count, 0)
    eta_days = math.ceil(remaining / DAILY_RATE) if remaining > 0 else 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    ascii_count = render_small_number(count)
    bar = progress_bar(pct)
    status = milestone(count)

    return f"""<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:00d4ff,100:7c3aed&height=220&section=header&text=FALCON&fontSize=80&fontColor=ffffff&fontAlignY=35&desc=High-Altitude%20Commit%20Engine&descSize=18&descAlignY=55&animation=twinkling" width="100%"/>

<br>

[![Commits](https://img.shields.io/github/commit-activity/w/elixpo/falcon?style=for-the-badge&color=00d4ff&label=Weekly%20Commits)](https://github.com/elixpo/falcon/commits/main)
[![Last Commit](https://img.shields.io/github/last-commit/elixpo/falcon?style=for-the-badge&color=7c3aed)](https://github.com/elixpo/falcon)
[![Target](https://img.shields.io/badge/Target-2M_Commits-22c55e?style=for-the-badge)](https://github.com/elixpo/falcon)

<br>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=elixpoo&repo=falcon&theme=react-dark&hide_border=true&area=true&custom_title=Falcon%20Commit%20Activity" width="95%"/>

<br>

<table>
<tr><td>

```
{ascii_count}
```

</td></tr>
</table>

### `{bar}` &nbsp; **{pct:.2f}%**

<br>

| | | |
|:---:|:---:|:---:|
| **{count:,}** | of | **{target:,}** |
| Remaining | | **{remaining:,}** |
| ETA | | **~{eta_days} days** |
| Status | | {status} |
| Updated | | `{now}` |

<br>

*Falcon doesn't rest. Falcon commits.*

<br>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7c3aed,50:00d4ff,100:0d1117&height=120&section=footer" width="100%"/>

</div>
"""


if __name__ == "__main__":
    count = get_commit_count()
    readme = generate_readme(count)
    with open("README.md", "w") as f:
        f.write(readme)
    print(f"README updated: {count:,} / {TARGET:,}")
