@echo off
REM 가상환경 활성화
call C:\Users\sw126\my_flask_app\venv\Scripts\activate.bat

REM Flask 애플리케이션이 있는 디렉토리로 이동
cd C:\Users\sw126\my_flask_app

REM 필요한 패키지 설치 (한 번만 실행하면 됩니다)
pip install markdown2

REM Flask 서버 실행
python app.py

pause
