from flask import Flask
from celery import Celery

app = Flask(__name__)
celery = Celery(app.name, broker='redis://localhost:6379/0')

@celery.task(name="mytasks.process_idea")
def process_idea(idea):
    with app.app_context():
        print(f"Processing idea: {idea}")
        # 추가 로직 작성
        return idea
