FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir celery==5.4.0 redis==5.0.4
COPY producer.py .

# default cmd is set by compose `entrypoint`
