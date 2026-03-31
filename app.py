from flask import Flask, request, jsonify, render_template
import ICAO_code_translate
import METAR_translate
import re
import api

# ------------------ Flask 应用 ------------------
app = Flask(__name__)
# 设置静态文件和模板目录（默认即可）

# 初始化 ICAO 翻译器（假设 airports.json 和 country_multilingual.csv 在程序同目录）
translator = ICAO_code_translate.ICAOTranslator(data_dir='data')

@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')

@app.route('/api/icao', methods=['POST'])
def icao_query():
    """ICAO 查询 API"""
    data = request.get_json()
    icao_code = data.get('icao', '').strip().upper()
    if not icao_code:
        return jsonify({'error': '请输入 ICAO 代码'}), 400
    # 调用 translator 的 translate 方法，该方法返回字符串（原来打印的文本）
    # 为了前端方便，我们也可以修改为返回字典，但为了快速适配，我们可以返回原文本
    result = translator.translate(icao_code)
    return jsonify({'result': result})

@app.route('/api/metar', methods=['POST'])
def metar_translate():
    """METAR 报文翻译 API"""
    data = request.get_json()
    metar = data.get('metar', '').strip()
    if not metar:
        return jsonify({'error': '请输入 METAR 报文'}), 400
    # 调用 parse_metar 函数，该函数返回字典（之前我们实现的 parse_metar 返回字典）
    parsed = METAR_translate.parse_metar(metar)
    result = METAR_translate.translate_codes(parsed)
    # 将字典转为字符串（保留换行）返回给前端，也可以直接返回字典让前端渲染
    # 为了简单，我们返回字符串
    # result_str = "\n".join([f"{k}: {v}" for k, v in parsed.items() if v])
    # return jsonify({'result': result_str})
    return jsonify({'result': result})

@app.route('/api/fetch_metar', methods=['POST'])
def fetch_metar_api():
    data = request.get_json()
    icao = data.get('icao', '').strip()
    if not icao:
        return jsonify({'error': '请输入 ICAO 代码'}), 400
    if not re.match(r'^[A-Z]{4}$', icao.upper()):
        return jsonify({'error': 'ICAO 代码应为 4 个大写字母'}), 400

    # 调用我们上面定义的函数
    raw_data = api.fetch_metar(icao, raw=False)
    if raw_data is None:
        return jsonify({'error': '获取 METAR 失败，请检查网络或 ICAO 代码'}), 500

    if not raw_data:
        return jsonify({'error': f'未找到 {icao} 的 METAR 报文'}), 404

    # 返回第一条报文（通常只有一条）
    metar_str = raw_data[0]
    return jsonify({'metar': metar_str})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)