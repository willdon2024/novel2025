from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密

MOONSHOT_API_URL = "https://api.moonshot.cn/v1/chat/completions"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'api_key' not in session:
            return jsonify({'error': '请先验证API Key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify_api_key', methods=['POST'])
def verify_api_key():
    api_key = request.json.get('api_key')
    if not api_key:
        return jsonify({'success': False, 'error': '请提供API Key'}), 400

    # 构建测试请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "user",
                "content": "你好"
            }
        ]
    }

    try:
        response = requests.post(MOONSHOT_API_URL, headers=headers, json=data)
        response.raise_for_status()
        session['api_key'] = api_key
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/generate_background', methods=['POST'])
@require_api_key
def generate_background():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': '请输入小说标题'}), 400

    prompt = f"""请根据小说标题《{title}》生成详细的故事背景和主要人物设定，格式如下：

[背景]
- 时代背景
- 地理环境
- 社会状况
- 重要事件

[人物]
- 主要人物的姓名、年龄、身份
- 性格特点
- 人物关系
- 个人经历

请确保背景合理，人物丰满，为后续故事发展埋下伏笔。直接输出内容，不要加其他解释。"""

    try:
        response = requests.post(
            MOONSHOT_API_URL,
            headers={
                "Authorization": f"Bearer {session['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "moonshot-v1-8k",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # 分离背景和人物信息
        sections = content.split('[人物]')
        background = sections[0].replace('[背景]', '').strip()
        characters = sections[1].strip() if len(sections) > 1 else ''
        
        return jsonify({
            'background': background,
            'characters': characters
        })
    except Exception as e:
        return jsonify({'error': f'生成背景时出错: {str(e)}'}), 500

@app.route('/generate_outline', methods=['POST'])
@require_api_key
def generate_outline():
    title = request.json.get('title')
    background_edit = request.json.get('background_edit', '')
    
    if not title:
        return jsonify({'error': '请输入小说标题'}), 400

    prompt = f"""基于小说标题《{title}》和以下修改建议，生成一个详细的故事大纲：

修改建议：
{background_edit}

请生成一个包含以下内容的大纲：
1. 故事主线
2. 重要转折点
3. 次要情节线
4. 结局设计

请确保大纲结构完整，情节连贯，富有戏剧性。直接输出内容，不要加其他解释。"""

    try:
        response = requests.post(
            MOONSHOT_API_URL,
            headers={
                "Authorization": f"Bearer {session['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "moonshot-v1-8k",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        outline = response.json()['choices'][0]['message']['content']
        return jsonify({'outline': outline})
    except Exception as e:
        return jsonify({'error': f'生成大纲时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 