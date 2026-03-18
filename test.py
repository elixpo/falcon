#!/usr/bin/env python3
"""
GitHub Contribution Graph Simulator
Previews how the '2026' pattern will appear on elixpoo's profile.
Renders a 53x7 grid matching GitHub's exact layout with ANSI colors.

Usage:
    python3 test.py                  # Full 2M simulation (10 sessions)
    python3 test.py 200000 1         # Quick preview: 1 session of 200k
    python3 test.py 2000000 10       # Full run: 10 sessions of 200k
"""

import sys
from datetime import datetime, timedelta
from collections import Counter

from falcon.engine import build_2026_pattern, generate_2026_timestamps
from falcon.config import load_config


# ANSI colors matching GitHub's contribution graph
R = "\033[0m"
COLORS = {
    0: "\033[48;2;22;27;34m",     # #161b22 — empty
    1: "\033[48;2;14;68;41m",     # #0e4429 — low
    2: "\033[48;2;0;109;50m",     # #006d32 — medium
    3: "\033[48;2;38;166;65m",    # #26a641 — bright
    4: "\033[48;2;57;211;83m",    # #39d353 — max
}
OUTSIDE = "\033[48;2;13;17;23m"   # outside year range
BLK = "  "                        # one square = 2 chars with bg color
DIM = "\033[2m"
BOLD = "\033[1m"


def intensity(count, q):
    if count == 0:
        return 0
    if count <= q[0]:
        return 1
    if count <= q[1]:
        return 2
    if count <= q[2]:
        return 3
    return 4


def quartiles(day_counts):
    vals = sorted(v for v in day_counts.values() if v > 0)
    if not vals:
        return [0, 0, 0]
    n = len(vals)
    return [vals[n // 4], vals[n // 2], vals[3 * n // 4]]


def simulate(total_commits=None, sessions=None):
    config = load_config()
    target = config["target_commits"]
    daily = config["daily_target"]

    if sessions is None:
        sessions = target // daily
    if total_commits is None:
        total_commits = target

    per_session = total_commits // sessions

    # GitHub graph geometry
    base_sun = datetime(2025, 12, 28)  # Sunday before Jan 1, 2026
    y_start = datetime(2026, 1, 1).date()
    y_end = datetime(2026, 12, 31).date()
    weeks = 53
    bright = build_2026_pattern()
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Header
    print(f"\n{BOLD}{'═' * 62}{R}")
    print(f"{BOLD}  FALCON — GitHub Contribution Graph Simulator{R}")
    print(f"{BOLD}{'═' * 62}{R}")
    print(f"  Target:     {total_commits:>12,} commits")
    print(f"  Sessions:   {sessions:>12} × {per_session:,} each")
    print(f"  Pattern:    '2026' ({len(bright)} bright days, 8:1 ratio)")
    print(f"  Committer:  elixpoo <elixpoo@gmail.com>")
    print()

    # Generate timestamps across all sessions
    day_counts = Counter()
    sys.stdout.write("  Simulating: ")
    sys.stdout.flush()
    for s in range(sessions):
        for t in generate_2026_timestamps(per_session):
            day_counts[t.date()] += 1
        sys.stdout.write("█")
        sys.stdout.flush()
    print(f"  ({sessions} sessions)")
    print()

    q = quartiles(day_counts)
    bright_avg = sum(day_counts[d] for d in bright) / len(bright)
    bg_days = [d for d in day_counts if d not in bright]
    bg_avg = sum(day_counts[d] for d in bg_days) / len(bg_days) if bg_days else 0

    print(f"  Quartiles:  Q1={q[0]:,}  Q2={q[1]:,}  Q3={q[2]:,}")
    print(f"  Bright avg: {bright_avg:,.0f}/day   Background avg: {bg_avg:,.0f}/day   Ratio: {bright_avg / bg_avg:.1f}x")
    print(f"  Total:      {sum(day_counts.values()):,}")
    print()

    # ── Month header ──
    hdr = "       "
    prev_m = -1
    for w in range(weeks):
        d = (base_sun + timedelta(days=w * 7)).date()
        if d.year == 2026 and d.month != prev_m:
            m = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d.month - 1]
            hdr += m
            prev_m = d.month
            # pad to next month
            for w2 in range(w + 1, weeks):
                d2 = (base_sun + timedelta(days=w2 * 7)).date()
                if d2.year == 2026 and d2.month != prev_m:
                    gap = (w2 - w) * 2 - len(m)
                    hdr += " " * max(0, gap)
                    break
        elif d.year < 2026:
            hdr += "  "
    print(f"  {DIM}{hdr}{R}")

    # ── Full year graph ──
    for row in range(7):
        lbl = f"  {DIM}{day_labels[row]}{R} " if row % 2 == 1 else "      "
        line = lbl
        for w in range(weeks):
            date = (base_sun + timedelta(days=w * 7 + row)).date()
            if date < y_start or date > y_end:
                line += f"{OUTSIDE}{BLK}{R}"
            else:
                c = day_counts.get(date, 0)
                line += f"{COLORS[intensity(c, q)]}{BLK}{R}"
        print(line)

    # Legend
    print()
    print(f"  {DIM}Less{R} ", end="")
    for lv in range(5):
        print(f"{COLORS[lv]}{BLK}{R}", end="")
    print(f" {DIM}More{R}")
    print()

    # ── Zoomed view: pattern area (weeks 13–40) ──
    z_start, z_end = 13, 40
    print(f"  {BOLD}Zoomed: '2026' pattern area (weeks {z_start}–{z_end}){R}")
    print()
    for row in range(7):
        line = "    "
        pat = "    "
        for w in range(z_start, z_end):
            date = (base_sun + timedelta(days=w * 7 + row)).date()
            if date < y_start or date > y_end:
                line += f"{OUTSIDE}{BLK}{R}"
            else:
                c = day_counts.get(date, 0)
                line += f"{COLORS[intensity(c, q)]}{BLK}{R}"
            if date in bright:
                pat += "██"
            else:
                pat += "░░"
        print(f"{line}  {DIM}{pat}{R}")

    print()
    zw = (z_end - z_start) * 2
    print(f"    {'▲ Simulated':^{zw}}  {DIM}{'▲ Target pattern':^{zw}}{R}")
    print()


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else None
    sess = int(sys.argv[2]) if len(sys.argv) > 2 else None
    simulate(total, sess)
