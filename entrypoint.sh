#!/bin/bash
set -e

echo "╔══════════════════════════════════════════╗"
echo "║     FALCON CONTAINER STARTING            ║"
echo "╚══════════════════════════════════════════╝"

# Configure git identity
git config --global user.name "${GIT_USER_NAME:-Circuit-Overtime}"
git config --global user.email "${GIT_USER_EMAIL:-ayushbhatt633@gmail.com}"
git config --global credential.helper store

# Setup git credentials for push
if [ -n "$GITHUB_TOKEN" ]; then
    echo "https://${GIT_USER_NAME:-Circuit-Overtime}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
    echo "[falcon] Git credentials configured"
fi

# Clone or use mounted repo
if [ -d "/repo/.git" ]; then
    echo "[falcon] Using mounted repo at /repo"
    cd /repo
else
    echo "[falcon] Cloning repo..."
    git clone "https://${GIT_USER_NAME:-Circuit-Overtime}:${GITHUB_TOKEN}@github.com/elixpo/falcon.git" /repo
    cp -r /app/falcon /repo/falcon
    cp /app/config.json /repo/config.json
    cd /repo
fi

echo "[falcon] Current commit count: $(git rev-list --count HEAD)"

# Run mode
case "${MODE:-loop}" in
    once)
        echo "[falcon] Running single session..."
        python3 -m falcon
        ;;
    loop)
        echo "[falcon] Starting loop mode — one session per day at a random time"
        while true; do
            # Check if target reached
            COUNT=$(git rev-list --count HEAD)
            TARGET=$(python3 -c "import json; print(json.load(open('config.json'))['target_commits'])")
            if [ "$COUNT" -ge "$TARGET" ]; then
                echo "[falcon] Target reached! $COUNT/$TARGET. Stopping."
                break
            fi

            echo "[falcon] Starting session at $(date)"
            python3 -m falcon || echo "[falcon] Session failed, will retry next cycle"

            # Sleep 18-24h so we guarantee one session every calendar day
            # 18h base + 0-6h jitter = 18-24h between sessions
            BASE=$((18 * 3600))
            JITTER=$((RANDOM % (6 * 3600)))
            SLEEP=$((BASE + JITTER))
            HOURS=$((SLEEP / 3600))
            MINS=$(( (SLEEP % 3600) / 60 ))
            echo "[falcon] Next session in ${HOURS}h ${MINS}m ($(date -d "+${SLEEP} seconds" 2>/dev/null || echo 'check logs'))"
            sleep $SLEEP
        done
        ;;
    *)
        echo "[falcon] Unknown mode: $MODE"
        exit 1
        ;;
esac
