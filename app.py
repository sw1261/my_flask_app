from flask import Flask, request, render_template, jsonify, redirect, url_for
import openai
import os
import markdown2
from dotenv import load_dotenv

load_dotenv()  # .env 파일의 환경 변수를 로드합니다.

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키를 불러옵니다.

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/validate_idea', methods=['POST'])
def validate_idea():
    idea = request.form['idea']
    return redirect(url_for('loading', idea=idea))

@app.route('/loading')
def loading():
    idea = request.args.get('idea')
    return render_template('loading.html', idea=idea)

@app.route('/process', methods=['GET'])
def process():
    idea = request.args.get('idea')
    prompt = f"""
    사업 아이디어를 검증하기 위해 다음의 질문들에 대한 분석을 수행해주세요.

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
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        result = response['choices'][0]['message']['content'].strip()
        html_result = markdown2.markdown(result)
    except openai.error.OpenAIError as e:
        print(f"API error: {e}")
        return jsonify({"error": "API error, please try again later"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500

    return jsonify({"result": html_result})

@app.route('/result')
def result():
    result = request.args.get('result')
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
