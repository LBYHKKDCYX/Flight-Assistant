from flask import Flask, request, jsonify, render_template
from flasgger import Swagger, swag_from
import ICAO_code_translate
import METAR_translate
import re
import api

# ------------------ Flask 应用 ------------------
app = Flask(__name__)
# 设置静态文件和模板目录（默认即可）
swagger = Swagger(app)

# 初始化 ICAO 翻译器（数据 airports.json 和 country_multilingual.csv 存放在 data/ 目录下）
translator = ICAO_code_translate.ICAOTranslator(data_dir='data')

@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')

# ------------------ 前端专用 API（返回格式化字符串，供 Web 界面使用） ------------------
@app.route('/api_web/icao', methods=['POST'])
def icao_query():
    """ICAO 查询 API（返回格式化字符串）"""
    data = request.get_json()
    icao_code = data.get('icao', '').strip().upper()
    if not icao_code:
        return jsonify({'error': '请输入 ICAO 代码'}), 400
    # 调用 translator 的 translate 方法，该方法返回字符串（原来打印的文本）
    result = translator.translate(icao_code)
    return jsonify({'result': result})

@app.route('/api_web/metar', methods=['POST'])
def metar_translate():
    """METAR 报文翻译 API（返回格式化字符串）"""
    data = request.get_json()
    metar = data.get('metar', '').strip()
    if not metar:
        return jsonify({'error': '请输入 METAR 报文'}), 400
    parsed = METAR_translate.parse_metar(metar)
    result = METAR_translate.translate_codes(parsed)
    return jsonify({'result': result})

@app.route('/api_web/fetch_metar', methods=['POST'])
def fetch_metar_api():
    """通过 ICAO 获取实时 METAR 原始报文"""
    data = request.get_json()
    icao = data.get('icao', '').strip()
    if not icao:
        return jsonify({'error': '请输入 ICAO 代码'}), 400
    if not re.match(r'^[A-Z]{4}$', icao.upper()):
        return jsonify({'error': 'ICAO 代码应为 4 个大写字母'}), 400

    raw_data = api.fetch_metar(icao, raw=False)
    if raw_data is None:
        return jsonify({'error': '获取 METAR 失败，请检查网络或 ICAO 代码'}), 500
    if not raw_data:
        return jsonify({'error': f'未找到 {icao} 的 METAR 报文'}), 404

    # 返回第一条报文（通常只有一条）
    metar_str = raw_data[0]
    return jsonify({'metar': metar_str})

# ------------------ 通用 API（返回 JSON，可配置输出格式，供开发者使用） ------------------
# ------------------ 通用 API（自动生成文档） ------------------
@app.route('/api/v1/icao/<icao>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'icao',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ICAO 代码（4字母）'
        },
        {
            'name': 'format',
            'in': 'query',
            'type': 'string',
            'enum': ['dict', 'string'],
            'default': 'dict',
            'description': '返回格式：dict 返回原始字典，string 返回格式化文本（国家和时区会翻译）'
        }
    ],
    'responses': {
        '200': {
            'description': '成功',
            'examples': {
                'application/json': {
                    'code': 200,
                    'message': 'success',
                    'data': {
                        'icao': 'ZBAA',
                        'iata': 'PEK',
                        'name': 'Beijing Capital International Airport',
                        'city': 'Beijing',
                        'country': 'CN',
                        'elevation_ft': 116,
                        'lat': 40.0801010132,
                        'lon': 116.5849990845,
                        'tz': 'Asia/Shanghai'
                    }
                }
            }
        },
        '404': {'description': 'ICAO 代码不存在'}
    }
})
def api_icao(icao):
    """
    查询 ICAO 机场信息
    参数: ?format=dict|string  默认 dict
    """
    fmt = request.args.get('format', 'dict').lower()
    icao = icao.strip().upper()
    if icao not in translator.airports:
        return jsonify({'code': 404, 'message': f'ICAO {icao} not found'}), 404

    if fmt == 'string':
        result = translator.translate(icao)
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:  # dict
        info = translator.airports[icao]
        data = {
            'icao': icao,
            'iata': info.get('iata', ''),
            'name': info.get('name', ''),
            'city': info.get('city', ''),
            'state': info.get('state', ''),
            'country': info.get('country', ''),
            'elevation_ft': info.get('elevation'),
            'lat': info.get('lat'),
            'lon': info.get('lon'),
            'tz': info.get('tz', '')
        }
        return jsonify({'code': 200, 'message': 'success', 'data': data})


@app.route('/api/v1/metar/translate', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'metar': {'type': 'string', 'example': 'ZSSS 251200Z 12005KT 9999 FEW020 18/12 Q1018 NOSIG'}
                },
                'required': ['metar']
            }
        },
        {
            'name': 'format',
            'in': 'query',
            'type': 'string',
            'enum': ['dict', 'string'],
            'default': 'dict',
            'description': '译文返回格式：dict 返回解析后的字典，string 返回格式化文本'
        }
    ],
    'responses': {
        '200': {'description': '翻译成功'},
        '400': {'description': '请求体缺少 metar 字段或内容为空'}
    }
})
def api_metar_translate():
    """
    翻译 METAR 报文
    参数: ?format=dict|string  默认 dict
    请求体: {"metar": "..."}
    """
    fmt = request.args.get('format', 'dict').lower()
    data = request.get_json()
    if not data or 'metar' not in data:
        return jsonify({'code': 400, 'message': 'Missing metar field'}), 400
    metar = data['metar'].strip()
    if not metar:
        return jsonify({'code': 400, 'message': 'METAR cannot be empty'}), 400

    parsed = METAR_translate.parse_metar(metar)
    if fmt == 'string':
        result = METAR_translate.translate_codes(parsed)
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 200, 'message': 'success', 'data': parsed})


@app.route('/api/v1/metar/fetch/<icao>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'icao',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ICAO 代码'
        },
        {
            'name': 'raw',
            'in': 'query',
            'type': 'boolean',
            'default': False,
            'description': '是否返回原始 METAR 报文'
        },
        {
            'name': 'translated',
            'in': 'query',
            'type': 'boolean',
            'default': True,
            'description': '是否返回译文'
        },
        {
            'name': 'format',
            'in': 'query',
            'type': 'string',
            'enum': ['dict', 'string'],
            'default': 'dict',
            'description': '译文返回格式'
        }
    ],
    'responses': {
        '200': {'description': '成功获取并处理 METAR'},
        '404': {'description': '未找到该 ICAO 的 METAR 报文'},
        '500': {'description': '外部 API 请求失败'}
    }
})
def api_metar_fetch(icao):
    """
    获取实时 METAR 报文
    参数:
        raw: true/false  是否返回原始报文，默认 false
        translated: true/false  是否返回译文，默认 true
        format: dict|string  译文格式（仅当 translated=true 时生效），默认 dict
    """
    raw_flag = request.args.get('raw', 'false').lower() == 'true'
    translated_flag = request.args.get('translated', 'true').lower() == 'true'
    fmt = request.args.get('format', 'dict').lower()

    icao = icao.strip().upper()
    raw_data = api.fetch_metar(icao, raw=False)
    if raw_data is None:
        return jsonify({'code': 500, 'message': 'Failed to fetch METAR'}), 500
    if not raw_data:
        return jsonify({'code': 404, 'message': f'No METAR found for {icao}'}), 404

    metar_str = raw_data[0]
    result = {}

    if raw_flag:
        result['raw_metar'] = metar_str

    if translated_flag:
        parsed = METAR_translate.parse_metar(metar_str)
        if fmt == 'string':
            result['translated'] = METAR_translate.translate_codes(parsed)
        else:
            result['translated'] = parsed

    if not raw_flag and not translated_flag:
        return jsonify({'code': 400, 'message': 'At least one of raw or translated must be true'}), 400

    return jsonify({'code': 200, 'message': 'success', 'data': result})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)