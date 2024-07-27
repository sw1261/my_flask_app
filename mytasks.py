from celery import Celery
from flask import Flask

app = Flask(__name__)  # Create Flask app
celery = Celery('mytasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery.task(name="mytasks.process_idea")
def process_idea(idea):
    with app.app_context():  # Set Flask application context
        print(f"Processing idea: {idea}")
        # Add additional logic here
        return idea
