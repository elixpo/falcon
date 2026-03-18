import math
from datetime import datetime

from .ascii_art import render_small_number


def _progress_bar(pct, width=20):
    """Unicode progress bar."""
    filled = int(width * pct / 100)
    empty = width - filled
    return "█" * filled + "░" * empty


def _milestone_status(count):
    """Return the latest milestone reached."""
    milestones = [
        (1000000, "🏔️ ONE MILLION"),
        (750000, "🔥 750K"),
        (500000, "⚡ HALF MILLION"),
        (250000, "🚀 250K"),
        (100000, "✈️ 100K"),
        (50000, "🛫 50K"),
        (10000, "🦅 10K"),
    ]
    for threshold, label in milestones:
        if count >= threshold:
            return label
    return "🥚 WARMING UP"


def generate_readme(count, target):
    pct = min(count / target, 1.0) * 100 if target > 0 else 0
    remaining = max(target - count, 0)
    ascii_count = render_small_number(count)
    bar = _progress_bar(pct)
    milestone = _milestone_status(count)
    daily_rate = 200000
    eta_days = math.ceil(remaining / daily_rate) if remaining > 0 else 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

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
| Status | | {milestone} |
| Updated | | `{now}` |

<br>

*Falcon doesn't rest. Falcon commits.*

<br>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7c3aed,50:00d4ff,100:0d1117&height=120&section=footer" width="100%"/>

</div>
"""
