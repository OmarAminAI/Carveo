FROM python:3.12-slim

WORKDIR /app
COPY workers/ingestion/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && crawl4ai-setup
COPY workers/ingestion/worker ./worker
CMD ["python", "-m", "worker.main"]
