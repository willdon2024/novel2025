from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MOONSHOT_API_KEY = os.getenv('MOONSHOT_API_KEY')
MOONSHOT_API_URL = "https://api.moonshot.cn/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_novel', methods=['POST'])
def generate_novel():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': '请输入小说标题'}), 400

    # 构建提示词
    prompt = f"""请根据标题《{title}》写一个小说开头章节，要求：
    1. 字数在1000字左右
    2. 要有吸引人的情节
    3. 要有细腻的描写
    4. 要有合理的人物对话
    请直接输出小说内容，不要加其他解释。"""

    headers = {
        "Authorization": f"Bearer {MOONSHOT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(MOONSHOT_API_URL, headers=headers, json=data)
        response.raise_for_status()
        novel_content = response.json()['choices'][0]['message']['content']
        return jsonify({'content': novel_content})
    except Exception as e:
        return jsonify({'error': f'生成小说时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 