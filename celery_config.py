from celery import Celery
import os

def make_celery(app_name):
    celery = Celery(
        app_name,
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    return celery
