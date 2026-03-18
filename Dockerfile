FROM python:3.12-slim

WORKDIR /app

COPY brain/pyproject.toml brain/
RUN pip install --no-cache-dir aiosqlite "fastmcp>=0.1.0" "websockets>=12.0,<15.0"

COPY brain/jarvis_brain brain/jarvis_brain

ENTRYPOINT ["python", "-m", "jarvis_brain.mcp_server"]
