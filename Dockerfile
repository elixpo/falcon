FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cron \
    bc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY falcon/ falcon/
COPY scripts/ scripts/
COPY config.json .
COPY progress.txt .
COPY README.md .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
