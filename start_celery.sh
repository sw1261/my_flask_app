#!/bin/bash

# Start Celery worker
celery -A celery_worker.celery worker --loglevel=info -P eventlet
