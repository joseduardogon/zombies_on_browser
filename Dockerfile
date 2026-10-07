FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ZOB_DB_PATH=/data/zombies.db \
    ZOB_STATIC_DIR=/app/static
WORKDIR /app
RUN pip install --no-cache-dir "fastapi>=0.129,<0.130" "uvicorn>=0.40,<0.41"
COPY backend/app ./app
COPY --from=frontend /frontend/dist ./static
VOLUME /data
EXPOSE 7001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7001"]
