web: gunicorn -w 4 -b 0.0.0.0:8000 --timeout 300 app:app
worker: celery -A celery_worker.celery worker --loglevel=info
