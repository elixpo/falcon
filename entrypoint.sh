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

# Setup git credentials for push
if [ -n "$GITHUB_TOKEN" ]; then
    echo "https://${GIT_USER_NAME:-elixpoo}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
    echo "[falcon] Git credentials configured"
fi

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

export FALCON_REPO_DIR=/repo
echo "[falcon] Current commit count: $(git rev-list --count HEAD)"

# Run mode
case "${MODE:-loop}" in
    once)
        echo "[falcon] Running single session..."
        python3 -m falcon
        ;;
    loop)
        echo "[falcon] Starting daily loop — runs session, checks daily target"
        while true; do
            # Check if overall target reached
            COUNT=$(git rev-list --count HEAD)
            TARGET=$(python3 -c "import json; print(json.load(open('config.json'))['target_commits'])")
            if [ "$COUNT" -ge "$TARGET" ]; then
                echo "[falcon] Overall target reached! $COUNT/$TARGET. Stopping."
                break
            fi

            echo "[falcon] Starting session at $(date)"
            # run_session() handles daily target check internally
            # If today's target is already hit, it exits immediately
            python3 -m falcon || echo "[falcon] Session failed, will retry next cycle"

            # Sleep until next check — every 6h to catch the next day
            echo "[falcon] Next check in 6h ($(date -d '+6 hours' 2>/dev/null || echo 'check logs'))"
            sleep 21600
        done
        ;;
    *)
        echo "[falcon] Unknown mode: $MODE"
        exit 1
        ;;
esac
