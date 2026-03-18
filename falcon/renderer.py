from datetime import datetime

from .ascii_art import render_small_number
from .git import get_current_count


def generate_readme(count, target):
    pct = min(count / target, 1.0) * 100 if target > 0 else 0
    ascii_count = render_small_number(count)

    return f"""<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:00d4ff,100:7c3aed&height=220&section=header&text=FALCON&fontSize=80&fontColor=ffffff&fontAlignY=35&desc=High-Altitude%20Commit%20Engine&descSize=18&descAlignY=55&animation=twinkling" width="100%"/>

<br>

[![Commits](https://img.shields.io/github/commit-activity/w/elixpo/falcon?style=for-the-badge&color=00d4ff&label=Weekly%20Commits)](https://github.com/elixpo/falcon/commits/main)
[![Last Commit](https://img.shields.io/github/last-commit/elixpo/falcon?style=for-the-badge&color=7c3aed)](https://github.com/elixpo/falcon)

<br>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=elixpo&repo=falcon&theme=react-dark&hide_border=true&area=true&custom_title=Falcon%20Commit%20Activity" width="95%"/>

<br>

```
{ascii_count}
```

**{count:,}** / **{target:,}** &mdash; {pct:.2f}%

<br>

*Falcon doesn't rest. Falcon commits.*

<br>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7c3aed,50:00d4ff,100:0d1117&height=120&section=footer" width="100%"/>

</div>
"""
