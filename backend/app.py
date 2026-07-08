import re
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger, swag_from
from translator import ICAOTranslator, parse_metar, translate_codes
from utils import fetch_metar

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

translator = ICAOTranslator()

# ------------------ 前端专用 API ------------------
@app.route('/api_web/icao', methods=['POST'])
def icao_query():
    data = request.get_json()
    icao_code = data.get('icao', '').strip().upper()
    if not icao_code:
        return jsonify({'error': '请输入 ICAO 代码'}), 400
    result = translator.translate(icao_code)
    return jsonify({'result': result})


@app.route('/api_web/metar', methods=['POST'])
def metar_translate():
    data = request.get_json()
    metar = data.get('metar', '').strip()
    if not metar:
        return jsonify({'error': '请输入 METAR 报文'}), 400
    parsed = parse_metar(metar)
    result = translate_codes(parsed)
    return jsonify({'result': result})


@app.route('/api_web/suggest', methods=['GET'])
def suggest_icao():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 1:
        return jsonify({'suggestions': []})
    suggestions = translator.suggest(query)
    return jsonify({'suggestions': suggestions})


@app.route('/api_web/fetch_metar', methods=['POST'])
def fetch_metar_api():
    data = request.get_json()
    icao = data.get('icao', '').strip()
    if not icao:
        return jsonify({'error': '请输入 ICAO 代码'}), 400
    if not re.match(r'^[A-Z]{4}$', icao.upper()):
        return jsonify({'error': 'ICAO 代码应为 4 个大写字母'}), 400

    raw_data = fetch_metar(icao, raw=False)
    if raw_data is None:
        return jsonify({'error': '获取 METAR 失败，请检查网络或 ICAO 代码'}), 500
    if not raw_data:
        return jsonify({'error': f'未找到 {icao} 的 METAR 报文'}), 404

    metar_str = raw_data[0]
    return jsonify({'metar': metar_str})


# ------------------ 通用 API ------------------
@app.route('/api/v1/icao/<icao>', methods=['GET'])
@swag_from({
    'parameters': [
        {'name': 'icao', 'in': 'path', 'type': 'string', 'required': True, 'description': 'ICAO 代码（4字母）'},
        {'name': 'format', 'in': 'query', 'type': 'string', 'enum': ['dict', 'string'], 'default': 'dict', 'description': '返回格式'}
    ],
    'responses': {'200': {'description': '成功'}, '404': {'description': 'ICAO 代码不存在'}}
})
def api_icao(icao):
    fmt = request.args.get('format', 'dict').lower()
    icao = icao.strip().upper()
    if icao not in translator.airports:
        return jsonify({'code': 404, 'message': f'ICAO {icao} not found'}), 404

    if fmt == 'string':
        result = translator.translate(icao)
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        info = translator.airports[icao]
        data = {
            'icao': icao, 'iata': info.get('iata', ''), 'name': info.get('name', ''),
            'city': info.get('city', ''), 'state': info.get('state', ''),
            'country': info.get('country', ''), 'elevation_ft': info.get('elevation'),
            'lat': info.get('lat'), 'lon': info.get('lon'), 'tz': info.get('tz', '')
        }
        return jsonify({'code': 200, 'message': 'success', 'data': data})


# ------------------ 生产环境托管前端静态文件 ------------------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist')


@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    # SPA fallback: 非静态资源返回 index.html
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/api/v1/metar/translate', methods=['POST'])
@swag_from({
    'parameters': [
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object', 'properties': {'metar': {'type': 'string'}}, 'required': ['metar']
        }},
        {'name': 'format', 'in': 'query', 'type': 'string', 'enum': ['dict', 'string'], 'default': 'dict'}
    ],
    'responses': {'200': {'description': '翻译成功'}, '400': {'description': '请求体缺少 metar 字段'}}
})
def api_metar_translate():
    fmt = request.args.get('format', 'dict').lower()
    data = request.get_json()
    if not data or 'metar' not in data:
        return jsonify({'code': 400, 'message': 'Missing metar field'}), 400
    metar = data['metar'].strip()
    if not metar:
        return jsonify({'code': 400, 'message': 'METAR cannot be empty'}), 400

    parsed = parse_metar(metar)
    if fmt == 'string':
        result = translate_codes(parsed)
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 200, 'message': 'success', 'data': parsed})


@app.route('/api/v1/metar/fetch/<icao>', methods=['GET'])
@swag_from({
    'parameters': [
        {'name': 'icao', 'in': 'path', 'type': 'string', 'required': True, 'description': 'ICAO 代码'},
        {'name': 'raw', 'in': 'query', 'type': 'boolean', 'default': False, 'description': '是否返回原始 METAR 报文'},
        {'name': 'translated', 'in': 'query', 'type': 'boolean', 'default': True, 'description': '是否返回译文'},
        {'name': 'format', 'in': 'query', 'type': 'string', 'enum': ['dict', 'string'], 'default': 'dict', 'description': '译文返回格式'}
    ],
    'responses': {'200': {'description': '成功'}, '404': {'description': '未找到'}, '500': {'description': '请求失败'}}
})
def api_metar_fetch(icao):
    raw_flag = request.args.get('raw', 'false').lower() == 'true'
    translated_flag = request.args.get('translated', 'true').lower() == 'true'
    fmt = request.args.get('format', 'dict').lower()

    icao = icao.strip().upper()
    raw_data = fetch_metar(icao, raw=False)
    if raw_data is None:
        return jsonify({'code': 500, 'message': 'Failed to fetch METAR'}), 500
    if not raw_data:
        return jsonify({'code': 404, 'message': f'No METAR found for {icao}'}), 404

    metar_str = raw_data[0]
    result = {}

    if raw_flag:
        result['raw_metar'] = metar_str
    if translated_flag:
        parsed = parse_metar(metar_str)
        if fmt == 'string':
            result['translated'] = translate_codes(parsed)
        else:
            result['translated'] = parsed
    if not raw_flag and not translated_flag:
        return jsonify({'code': 400, 'message': 'At least one of raw or translated must be true'}), 400

    return jsonify({'code': 200, 'message': 'success', 'data': result})
