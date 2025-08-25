#!/bin/bash

# Wait for database to be ready
until python -c "
import time
import psycopg2
import os

db_url = os.getenv('DATABASE_URL')

for attempt in range(60):
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        exit(0)
    except Exception:
        if attempt < 11:
            time.sleep(5)
        else:
            exit(1)
"; do
    sleep 5
done

# Start Celery worker
exec celery -A tasks worker --loglevel=info
