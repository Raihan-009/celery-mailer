#!/usr/bin/env python3
"""
Send an enrol-confirmation e-mail task.

Usage inside container:
    python producer.py "<course name>" <user_id> <email>
"""
import sys
from celery import Celery

if len(sys.argv) != 4:
    print("Usage: python producer.py <course_name> <user_id> <email>")
    sys.exit(1)

course, uid, email = sys.argv[1], sys.argv[2], sys.argv[3]

BROKER = "redis://redis:6379/0"        # <─ service name reachable on network
celery = Celery("producer", broker=BROKER)

task_id = celery.send_task(
    "send_course_enrollment_email",
    args=[course, uid, email]
).id

print(f"Queued Celery task {task_id}")
