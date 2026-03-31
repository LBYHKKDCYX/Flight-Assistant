import requests
from requests.exceptions import RequestException

def fetch_metar(icao, raw=False):
    """
    从外部 API 获取指定 ICAO 的 METAR 报文。

    参数:
        icao: 机场 ICAO 代码（如 'ZBAA'）
        raw: 是否返回原始 JSON，False 时返回报文列表（默认为 False）

    返回:
        - 如果 raw=False，返回报文列表（list of str），例如 ['ZSSS ...']
        - 如果 raw=True，返回完整的 API 响应字典
        - 如果请求失败，返回 None
    """
    url = "https://isfpapi.flyisfp.com/api/metar"
    params = {
        "icao": icao.upper(),
        "raw": str(raw).lower()  # API 要求布尔值字符串 'true'/'false'
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()  # 非 2xx 状态码抛出异常
        data = resp.json()
        if not data.get("code") == "GET_METAR":
            # 接口返回错误码
            print(data)
            print(f"API 返回错误: {data.get('message')}")
            return None
        return data.get("data", []) if not raw else data
    except RequestException as e:
        print(f"请求失败: {e}")
        return None