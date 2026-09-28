# 在 Growth Lab 仓库根目录构建：
#   docker build -f executors/wechat-mp-publish/deploy/Dockerfile -t wechat-publisher:latest .
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WECHAT_PUBLISH_HOST=0.0.0.0 \
    WECHAT_PUBLISH_PORT=8080 \
    WECHAT_PUBLISH_WORKDIR=/data/wechat-posts \
    WECHAT_TOKEN_CACHE_PATH=/data/wechat-token/access-token.json

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /data/wechat-posts /data/wechat-token \
    && chown -R app:app /app /data

COPY --chown=app:app executors/wechat-mp-publish/scripts/ ./executors/wechat-mp-publish/scripts/
COPY --chown=app:app executors/wechat-article-compose/scripts/ ./executors/wechat-article-compose/scripts/

USER app

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=3).read()"

CMD ["python", "executors/wechat-mp-publish/scripts/server.py"]
