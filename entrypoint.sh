#!/bin/bash
set -e

echo "╔══════════════════════════════════════════╗"
echo "║     FALCON CONTAINER STARTING            ║"
echo "╚══════════════════════════════════════════╝"

# Configure git identity as elixpoo
git config --global user.name "${GIT_USER_NAME:-elixpoo}"
git config --global user.email "${GIT_USER_EMAIL:-elixpoo@gmail.com}"
git config --global credential.helper store

# Git performance optimizations
git config --global gc.auto 0
git config --global core.preloadIndex true
git config --global core.fscache true
git config --global pack.threads 0
git config --global commit.gpgsign false
git config --global core.hooksPath /dev/null

# Clone or use mounted repo
if [ -d "/repo/.git" ]; then
    echo "[falcon] Using mounted repo at /repo"
    cd /repo
else
    echo "[falcon] Cloning repo..."
    git clone "https://${GIT_USER_NAME:-elixpoo}:${GITHUB_TOKEN}@github.com/elixpo/falcon.git" /repo
    cp -r /app/falcon /repo/falcon
    cp /app/config.json /repo/config.json
    cd /repo
fi

# Embed token directly in remote URL so push always works
if [ -n "$GITHUB_TOKEN" ]; then
    git remote set-url origin "https://${GIT_USER_NAME:-elixpoo}:${GITHUB_TOKEN}@github.com/elixpo/falcon.git"
    echo "[falcon] Git credentials configured (token in remote URL)"
fi

export FALCON_REPO_DIR=/repo
echo "[falcon] Current commit count: $(git rev-list --count HEAD)"

# Run mode
case "${MODE:-loop}" in
    once)
        echo "[falcon] Running single session..."
        python3 -m falcon
        ;;
    loop)
        echo "[falcon] Starting loop — 3 sessions/day, 500k each"
        while true; do
            # Check if overall target reached
            COUNT=$(git rev-list --count HEAD)
            TARGET=$(python3 -c "import json; print(json.load(open('config.json'))['target_commits'])")
            if [ "$COUNT" -ge "$TARGET" ]; then
                echo "[falcon] Overall target reached! $COUNT/$TARGET. Stopping."
                break
            fi

            for SESSION in 1 2 3; do
                echo "[falcon] Session $SESSION/3 starting at $(date)"

                # Reset state so each session can run
                python3 -c "
import json
try:
    with open('state.json','r') as f: s = json.load(f)
    s['last_session_date'] = None
    s['pending_session'] = None
    with open('state.json','w') as f: json.dump(s, f, indent=2)
except: pass
"
                python3 -m falcon || echo "[falcon] Session $SESSION failed, will retry"

                # 7h gap between sessions (3 × 7h ≈ 21h cycle, fits in a day)
                if [ "$SESSION" -lt 3 ]; then
                    echo "[falcon] Next session in 7h ($(date -d '+7 hours' 2>/dev/null || echo 'check logs'))"
                    sleep 25200
                fi
            done

            # Sleep remaining ~3h until next day cycle
            echo "[falcon] Next cycle in 3h ($(date -d '+3 hours' 2>/dev/null || echo 'check logs'))"
            sleep 10800
        done
        ;;
    *)
        echo "[falcon] Unknown mode: $MODE"
        exit 1
        ;;
esac
