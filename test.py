from falcon.engine import build_2026_pattern, generate_2026_timestamps
from falcon.config import load_config
from collections import Counter

config = load_config()
print(f'Target: {config["target_commits"]:,} total')
print(f'Daily cap: {config["daily_target"]:,} per session')
print(f'Sessions needed: {config["target_commits"] // config["daily_target"]}')
print()

# Simulate 10 sessions worth of timestamps (2M total)
bright = build_2026_pattern()
total_bright = 0
total_bg = 0

for session in range(10):
    ts = generate_2026_timestamps(200000)
    day_counts = Counter(t.date() for t in ts)
    b = sum(day_counts[d] for d in bright if d in day_counts)
    bg = sum(v for d, v in day_counts.items() if d not in bright)
    total_bright += b
    total_bg += bg

print(f'After 10 sessions (2M commits):')
print(f'  Bright days ({len(bright)} days): {total_bright:,} total commits (~{total_bright//len(bright):,}/day avg)')
print(f'  Background days (307 days): {total_bg:,} total commits (~{total_bg//307:,}/day avg)')
print(f'  Grand total: {total_bright + total_bg:,}')
print(f'  Ratio (bright:bg per day): {(total_bright/len(bright)) / (total_bg/307):.1f}x')
print()
print('The 2026 pattern will be clearly visible — bright days get 8x the commits.')
