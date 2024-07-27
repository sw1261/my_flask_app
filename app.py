import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template, jsonify, redirect, url_for, make_response
import openai
import os
import markdown2
import logging
from dotenv import load_dotenv
from fpdf import FPDF, HTMLMixin
import time
from celery_worker import make_celery
import requests
from mytasks import process_idea  # Import the task

# Load environment variables
load_dotenv()

# Flask application setup
app = Flask(__name__)
app.config.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)
celery = make_celery(app)
celery.conf.update(app.config)
celery.conf.task_default_queue = 'default'

# OpenAI API key setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Define PDF class
class MyFPDF(FPDF, HTMLMixin):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '아이디어 검증 결과', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Validate idea route
@app.route('/validate_idea', methods=['POST'])
def validate_idea():
    idea = request.form['idea']
    task = process_idea.apply_async(args=[idea])  # Call the task
    return redirect(url_for('loading', task_id=task.id))

# Loading page route
@app.route('/loading')
def loading():
    task_id = request.args.get('task_id')
    return render_template('loading.html', task_id=task_id)

# Process status route
@app.route('/process/<task_id>', methods=['POST', 'GET'])
def process(task_id):
    task = process_idea.AsyncResult(task_id)
    logging.debug(f"Task status: {task.state}")
    if task.state == 'SUCCESS':
        logging.debug(f"Task result: {task.result}")
        return jsonify(task.result)
    else:
        logging.debug(f"Current task state: {task.state}")
        return jsonify({'state': task.state})

# Result rendering route
@app.route('/result', methods=['POST'])
def result():
    try:
        result = request.form['result']
        idea = request.form['idea']
        logging.debug(f"Result for rendering: {result}")
        return render_template('result.html', result=result, idea=idea)
    except Exception as e:
        logging.error(f"Error rendering result: {e}")
        return jsonify({"error": f"Error rendering result: {str(e)}"}), 500

# PDF download route
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        result = request.form['result']
        idea = request.form.get('idea', '아이디어 제목 없음')
        logging.debug(f"Result for PDF: {result}")

        pdf = MyFPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"아이디어 제목: {idea}\n\n{result}")

        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers.set('Content-Disposition', 'attachment', filename='result.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500

# OpenAI API key test route
@app.route('/test_api_key')
def test_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    return jsonify({"api_key": api_key})

# Celery task definition
@celery.task(name="mytasks.process_idea")
def process_idea(idea):
    logging.debug(f"Idea received: {idea}")
    prompt = f"""
    다음은 사업 아이디어에 대한 분석입니다:

    아이디어: {idea}

    1. 시장성 및 타겟 분석
    - 이 아이디어가 진입할 수 있는 시장이 존재합니까? 존재한다면 시장의 규모는 어떻게 됩니까?
    - 타겟분포도는 어떻게 되나요?

    2. 기술적 실행 가능성
    - 이 아이디어를 구현하는데 예상되는 기술적 도전과 해결 방안은 무엇입니까?

    3. 법적 및 규제 준수
    - 해당 아이디어를 실행할 때 준수해야 할 주요 법적 및 규제 요구사항은 무엇입니까?

    4. 비용 및 예산
    - 해당 아이디어를 실행하는데 발생하는 예상 비용은 얼마입니까?
    - 이 프로젝트를 위한 예산을 어떻게 책정하고 관리할 수 있습니까?

    5. 사용자 피드백
    - 잠재 사용자로부터 피드백을 수집하는 가장 효과적인 방법은 무엇입니까?
    - 사용자 피드백을 제품 개발 및 개선에 어떻게 반영할 수 있습니까?

    6. 마케팅 및 시장 진입 전략
    - 이 제품을 성공적으로 시장에 출시하기 위한 마케팅 전략은 무엇입니까?
    - 경쟁 제품과의 차별화 전략은 무엇입니까?

    7. 비즈니스 모델 및 수익성
    - 이 아이디어의 수익 모델은 무엇입니까?
    - 이 비즈니스 모델의 장기적인 지속 가능성을 어떻게 평가할 수 있습니까?

    8. 데이터 분석
    - Fish Bone Diagram에 맞게 데이터를 작성해주세요.
    - Six Thinking Hats 모델을 대입하여 데이터 분석을 해주세요.
    - SWOT 분석을 해주세요.

    9. 사업 계획서 작성
    - 이 아이디어를 바탕으로 구체적인 사업 계획서를 작성해주세요. 사업의 목표, 전략, 실행 계획, 재무 계획 등을 포함해야 합니다.

    10. 위험 분석
    - 이 사업 아이디어와 관련된 잠재적 위험 요소를 식별하고, 이를 관리하기 위한 전략을 제안해주세요.
    """

    retries = 3
    for i in range(retries):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini-2024-07-18",
                    "messages": [
                        {"role": "system", "content": "당신은 도움이 되는 조수입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4000
                },
                timeout=300
            )
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content'].strip()
            html_result = markdown2.markdown(result)
            break
        except requests.exceptions.RequestException as e:
            logging.error(f"API error: {e}")
            if i < retries - 1:
                time.sleep(2 ** i)
            else:
                return {"error": f"API error, please try again later: {e}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error occurred: {str(e)}"}

    return {"result": html_result, "idea": idea}

# Run Flask application
if __name__ == '__main__':
    app.run(debug=True)
