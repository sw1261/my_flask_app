import eventlet
eventlet.monkey_patch()

from celery import Celery
import os
import mytasks  # Import the tasks module

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.getenv('result_backend', 'redis://localhost:6379/0'),
        broker=os.getenv('broker_url', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    return celery

class FakeApp:
    name = 'fake_app'
    import_name = name
    config = {
        'broker_url': os.getenv('broker_url', 'redis://localhost:6379/0'),
        'result_backend': os.getenv('result_backend', 'redis://localhost:6379/0')
    }

app = FakeApp()
celery = make_celery(app)
celery.conf.update(app.config)
celery.conf.task_default_queue = 'default'

print("celery_worker.py is being loaded")
print("celery worker is set up")
