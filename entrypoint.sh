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
        echo "[falcon] Starting loop — 2 sessions/day, 300k each"
        while true; do
            # Check if overall target reached
            COUNT=$(git rev-list --count HEAD)
            TARGET=$(python3 -c "import json; print(json.load(open('config.json'))['target_commits'])")
            if [ "$COUNT" -ge "$TARGET" ]; then
                echo "[falcon] Overall target reached! $COUNT/$TARGET. Stopping."
                break
            fi

            # Run session 1
            echo "[falcon] Session 1 starting at $(date)"
            python3 -m falcon || echo "[falcon] Session 1 failed, will retry"

            # Wait 10 hours then run session 2
            echo "[falcon] Session 2 in 10h ($(date -d '+10 hours' 2>/dev/null || echo 'check logs'))"
            sleep 36000

            # Reset daily state so session 2 can run on the same day
            python3 -c "
import json
try:
    with open('state.json','r') as f: s = json.load(f)
    s['last_session_date'] = None
    s['pending_session'] = None
    with open('state.json','w') as f: json.dump(s, f, indent=2)
except: pass
"

            # Run session 2
            echo "[falcon] Session 2 starting at $(date)"
            python3 -m falcon || echo "[falcon] Session 2 failed, will retry"

            # Wait until next day
            echo "[falcon] Next cycle in 10h ($(date -d '+10 hours' 2>/dev/null || echo 'check logs'))"
            sleep 36000
        done
        ;;
    *)
        echo "[falcon] Unknown mode: $MODE"
        exit 1
        ;;
esac
