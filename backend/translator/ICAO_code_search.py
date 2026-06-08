import json
import os
import csv
from datetime import datetime, timezone

# 如遇 时区库缺失：No module named 'tzdata' 请尝试pip install tzdata
# 如果还是报错就尝试使用Python路径（如“C:\Users\用户名\AppData\Local\Programs\Python\Python313\python.exe”）+“ -m pip install tzdata”
# Python路径可以通过
# import tzdata
# print(tzdata.__file__)
# 获取

# 尝试使用 Python 3.9+ 的 zoneinfo，否则使用 pytz
try:
    from zoneinfo import ZoneInfo  # Python 3.9 及以上
    USE_ZONEINFO = True
except ImportError:
    try:
        import pytz
        USE_ZONEINFO = False
    except ImportError:
        print("警告：需要 pytz 库来支持时区转换（Python < 3.9）。请安装：pip install pytz")
        pytz = None
        USE_ZONEINFO = None

class ICAOTranslator:
    def __init__(self, data_dir=None):
        """
        参数:
            data_dir: 存放所有数据文件的目录
        """
        if data_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(script_dir), 'data')
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(script_dir, data_dir) if not os.path.isabs(data_dir) else data_dir

        # 构建各数据文件的绝对路径
        airports_path = os.path.join(self.data_dir, 'airports.json')
        country_path = os.path.join(self.data_dir, 'country_translations.csv')
        tz_path = os.path.join(self.data_dir, 'timezone_translations.json')

        self.airports = {}
        self.country_names = {}
        self.tz_translations = {}

        self.load_database(airports_path)
        self.load_country_names(country_path)
        self.load_timezone_translations(tz_path)

    def load_database(self, json_file):
        """加载 JSON 文件到字典"""
        if not os.path.exists(json_file):
            print(f"错误：数据库文件 {json_file} 不存在")
            print("请从 https://github.com/mwgg/Airports 下载 airports.json 并放在 data/ 目录下")
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.airports = json.load(f)
            print(f"成功加载 {len(self.airports)} 个机场数据")
        except Exception as e:
            print(f"读取数据库失败：{e}")

    def load_country_names(self, country_file):
        """
        从 CSV 文件加载国家代码到中文名称的映射。
        文件格式应为：语言代码,语言名称,两字母代码,三字母代码,数字代码,国家中文名称
        例如：ZH-CN,CHINESE SIMPLIFIED,CN,CHN,156,中国
        """
        self.country_names = {}
        if not os.path.exists(country_file):
            print(f"警告：国家翻译文件 {country_file} 不存在，将显示原始代码")
            return

        try:
            with open(country_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig 自动处理 BOM 头
                reader = csv.reader(f)
                # 如果你的 CSV 文件第一行是标题，可以取消下一行的注释
                next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) < 6:
                        continue
                    code = row[2].strip()   # 第3列：两字母国家代码
                    name = row[5].strip()    # 第6列：国家中文名称
                    self.country_names[code] = name
            print(f"成功加载 {len(self.country_names)} 个国家翻译")
        except Exception as e:
            print(f"读取国家翻译文件失败：{e}")

    def load_timezone_translations(self, tz_file):
        """
        从 JSON 文件加载时区英文名到中文名的映射
        JSON 格式：{ "Asia/Shanghai": "中国标准时间 (上海)", ... }
        """
        self.tz_translations = {}
        if not os.path.exists(tz_file):
            print(f"警告：时区翻译文件 {tz_file} 不存在，将显示原始英文时区名")
            return
        try:
            with open(tz_file, 'r', encoding='utf-8') as f:
                self.tz_translations = json.load(f)
            print(f"成功加载 {len(self.tz_translations)} 个时区翻译")
        except Exception as e:
            print(f"读取时区翻译文件失败：{e}")

    def decimal_to_dms(self, decimal, is_latitude=True, precision=2):
        """
        将十进制度数转换为度分秒格式

        参数:
            decimal: float, 十进制度数，正数表示北纬/东经，负数表示南纬/西经
            is_latitude: bool, True表示纬度，False表示经度（仅用于确定方向字母）
            precision: int, 秒保留的小数位数，默认2

        返回:
            字符串，如 "39°54′15.12″N"
        """
        if decimal is None:
            return "未知"
        
        # 确定方向
        if decimal < 0:
            direction = 'S' if is_latitude else 'W'
            decimal = abs(decimal)
        else:
            direction = 'N' if is_latitude else 'E'
    
        # 提取度、分、秒
        degrees = int(decimal)
        remainder = (decimal - degrees) * 60
        minutes = int(remainder)
        seconds = (remainder - minutes) * 60
        seconds = round(seconds, precision)
    
        # 处理秒进位
        if seconds >= 60:
            seconds -= 60
            minutes += 1
        if minutes >= 60:
            minutes -= 60
            degrees += 1

        s_str = f"{seconds:.{precision}f}" if precision > 0 else str(int(seconds))
        return f"{str(degrees).strip()}°{str(minutes).strip()}′{s_str.strip()}″{direction}"

    def get_utc_offset(self, tz_name):
        """
        将 IANA 时区名称转换为当前 UTC 偏移量，格式如 'UTC+8' 或 'UTC-5'
        使用当前系统时间计算（考虑夏令时）
        """
        if not tz_name:
            return "时区未知"

        try:
            if USE_ZONEINFO:
                # Python 3.9+ 使用 zoneinfo
                tz = ZoneInfo(tz_name)
                now = datetime.now(tz)
                offset = now.utcoffset()
            else:
                # 使用 pytz
                if pytz is None:
                    return "时区库缺失"
                tz = pytz.timezone(tz_name)
                now = datetime.now(tz)
                offset = now.utcoffset()
            if offset is None:
                return "UTC"
            total_seconds = offset.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            sign = '+' if hours >= 0 else '-'

            if minutes == 0:
                return f"UTC{sign}{abs(hours)}"
            else:
                return f"UTC{sign}{abs(hours)}:{minutes:02d}"

        except Exception as e:
            return f"时区解析错误({tz_name})"
        
    def tz_to_chinese(self, tz_name, fallback=True):
        """
        将英文时区名称（IANA格式）转换为中文名称

        参数:
            tz_name: str, IANA时区名称，如 "Asia/Shanghai", "America/New_York"
            fallback: bool, 如果为True，找不到时返回原名称，否则返回None

        返回:
            str: 中文时区名称，或原名称/None
        """
        # 先从加载的映射表中查找
        if tz_name in self.tz_translations:
            return self.tz_translations[tz_name]

        # 尝试处理带偏移的格式（如 Etc/GMT+8），但这里简单处理
        if tz_name.startswith("Etc/GMT"):
            sign = tz_name[7:]
            if sign.startswith("-"):
                return f"UTC+{sign[1:]}"
            elif sign.startswith("+"):
                return f"UTC-{sign[1:]}"
            else:
                return "UTC"

        # 按斜杠拆分，尝试翻译国家/城市（简易版）
        parts = tz_name.split('/')
        if len(parts) == 2:
            continent, city = parts
            # 辅助：大洲英文转中文
            continent_map = {
                "Africa": "非洲", "America": "美洲", "Antarctica": "南极洲",
                "Asia": "亚洲", "Atlantic": "大西洋", "Australia": "澳洲",
                "Europe": "欧洲", "Indian": "印度洋", "Pacific": "太平洋"   
            }
            city_map = {
                "Shanghai": "上海", "Beijing": "北京", "Tokyo": "东京", "Seoul": "首尔",
                "New_York": "纽约", "Los_Angeles": "洛杉矶", "London": "伦敦", "Paris": "巴黎"
            }
            if city in city_map:
                return f"{continent_map.get(continent, continent)}/{city_map[city]}"
            else:
                return f"{continent_map.get(continent, continent)}/{city}"
        elif len(parts) == 3:
            # 如 America/Argentina/Buenos_Aires，简单拼接
            if not fallback:
                return "/".join([self.tz_to_chinese(parts[0], False), parts[1], parts[2]])
            else:
                return tz_name

        # 未找到，根据fallback决定返回
        if fallback:
            return tz_name
        else:
            return None

    def utc_to_local(self, icao_code, day, hour, minute):
        """
        将给定的 UTC 时间（日、时、分）转换为机场当地时区的时间
        :param icao_code: ICAO 代码
        :param day: 日 (1-31)
        :param hour: 时 (0-23)
        :param minute: 分 (0-59)
        :return: 当地时间的字符串描述
        """
        icao = icao_code.strip().upper()
        if icao not in self.airports:
            return f"未找到 ICAO 代码 {icao}"

        info = self.airports[icao]
        tz_name = info.get('tz')
        if not tz_name:
            return "该机场时区信息缺失，无法转换"

        try:
            # 获取当前 UTC 日期时间（用于获取当前年份和月份）
            now_utc = datetime.now(timezone.utc)
            # 用用户输入的日、时、分替换，注意月份使用当前月份
            dt_utc = datetime(now_utc.year, now_utc.month, day, hour, minute, tzinfo=timezone.utc)

            # 转换为当地时区
            if USE_ZONEINFO:
                local_tz = ZoneInfo(tz_name)
                dt_local = dt_utc.astimezone(local_tz)
            else:
                if pytz is None:
                    return "时区库缺失，无法转换"
                local_tz = pytz.timezone(tz_name)
                dt_local = dt_utc.astimezone(local_tz)

            return (f"UTC时间{dt_utc.strftime('%Y-%m-%d %H:%M %Z')}\n"
                    f"对应当地时间为: {dt_local.strftime('%Y-%m-%d %H:%M %Z')}（年月以当前UTC时间为根据）")
        except ValueError as e:
            return f"输入的时间无效：{e}"
        except ModuleNotFoundError as e:
            return f"时区库缺失：{e}"
        except Exception as e:
            return f"转换失败：{e}"
        
    def translate(self, icao_code):
        """
        根据 ICAO 代码查询机场信息，包含时区偏移
        """
        icao = icao_code.strip().upper()
        if icao in self.airports:
            info = self.airports[icao]
            icao = info.get('icao', '')
            iata = info.get('iata', '无IATA代码')
            # 提取需要显示的字段，并处理可能缺失的情况
            name = info.get('name', '未知')
            city = info.get('city', '未知')
            state = info.get('state', '')
            country_code = info.get('country', '')
            country_name = self.country_names.get(country_code, country_code)  # 有翻译就用，否则保留代码
            elevation_ft = info.get('elevation', '未知')
            elevation_m = round(float(elevation_ft) * 0.3048) if elevation_ft != '未知' else '未知'
            lat = info.get('lat', '未知')
            lat_dms = self.decimal_to_dms(float(info.get('lat')), True) if lat != '未知' else '未知'
            lon = info.get('lon', '未知')
            lon_dms = self.decimal_to_dms(float(info.get('lon')), False) if lon != '未知' else '未知'
            tz = info.get('tz', '')
            tz_chinese = self.tz_to_chinese(tz, True)

            # 获取 UTC 偏移
            utc_offset = self.get_utc_offset(tz) if tz else "时区信息缺失"

            # 组装输出
            result = f"机场名称：{name}"
            result += f"\nICAO代码：{icao}"
            if iata:
                result += f"\nIATA代码：{iata}"
            else:
                result += f"\nIATA代码：无IATA代码"
            result += f"\n所在城市：{city}"
            if state:
                result += f" ({state})"
            result += f"\n所在国家：{country_name}"
            result += f"\n海拔：{elevation_ft}英尺，{elevation_m}米"
            result += f"\n纬度：{lat}（{lat_dms}）"
            result += f"\n经度：{lon}（{lon_dms}）"
            result += f"\n时区：{tz_chinese} ({utc_offset})"
            return result
        else:
            # 未找到时尝试解释 ICAO 前缀
            prefix_hint = self.get_region_by_prefix(icao[:2])
            if prefix_hint:
                return f"未找到 ICAO 代码 {icao}，但前缀 {icao[:2]} 对应 {prefix_hint}"
            return f"未找到 ICAO 代码 {icao} 对应的机场"

    def get_region_by_prefix(self, prefix):
        """
        根据 ICAO 代码前两位解释所属区域/国家（参考 ICAO 分配规则）
        """
        prefix_map = {
            'Z': '中国',
            'ZB': '中国华北', 'ZG': '中国华南', 'ZH': '中国东北',
            'ZJ': '中国华东', 'ZL': '中国西北', 'ZP': '中国西南',
            'ZS': '中国华东', 'ZU': '中国西南', 'ZW': '中国新疆',
            'K': '美国本土', 'C': '加拿大', 'E': '北欧', 'L': '南欧',
            'B': '冰岛/科索沃', 'R': '韩国/日本', 'V': '东南亚',
            'Y': '澳大利亚', 'O': '中东', 'H': '东北非', 'F': '中南非',
            'S': '南美', 'T': '加勒比地区', 'U': '俄罗斯/独联体',
            'W': '东南亚', 'P': '太平洋地区'
        }
        if prefix in prefix_map:
            return prefix_map[prefix]
        if prefix[0] in prefix_map:
            return prefix_map[prefix[0]] + "（区域）"
        return None

def main():
    print("ICAO机场代码翻译器 (基于 mwgg_airports 数据库，支持时区偏移)")
    print("-" * 60)
    print("请将 airports.json, country_multilingual.csv, timezone_translations.json 放入 data/ 目录下")
    print("输入 ICAO 代码查询，输入 quit 退出\n")

    translator = ICAOTranslator(data_dir='data')

    while True:
        code = input("请输入 ICAO 代码: ").strip()
        if code.lower() in ('quit', 'exit', 'q'):
            break
        if not code:
            continue

        result = translator.translate(code)
        print(f"\n{result}\n")

        # 测试用
        break

if __name__ == '__main__':
    main()