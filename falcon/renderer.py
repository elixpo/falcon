from datetime import datetime

from .ascii_art import BANNER, render_ascii_number


def make_progress_bar(current, target, width=40):
    pct = min(current / target, 1.0)
    filled = int(width * pct)
    empty = width - filled
    bar = "\u2588" * filled + "\u2591" * empty
    return f"  {bar}  {pct * 100:.2f}%"


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
