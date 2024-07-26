from celery import Celery
from flask import Flask

app = Flask(__name__)  # Flask 앱 생성
celery = Celery('mytasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery.task(name="mytasks.process_idea")
def process_idea(idea):
    with app.app_context():  # Flask 애플리케이션 컨텍스트 설정
        print(f"Processing idea: {idea}")
        # 필요한 추가 로직을 여기에 넣습니다.
        return idea
