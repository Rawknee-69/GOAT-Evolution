FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"
WORKDIR /app
COPY --chown=appuser pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system --no-cache-dir -e .
COPY --chown=appuser backend/ ./backend/
COPY --chown=appuser openenv.yaml ./
COPY --chown=appuser --from=frontend-builder /frontend/dist ./frontend/dist
ENV PYTHONPATH="/app"
ENV PORT=7860
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=10s --start-period=25s --retries=3 CMD curl -f http://localhost:7860/health || exit 1
CMD ["uvicorn", "backend.server.app:app", "--host", "0.0.0.0", "--port", "7860"]
