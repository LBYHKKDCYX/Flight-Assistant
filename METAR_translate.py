import re
import ICAO_code_translate

translator = ICAO_code_translate.ICAOTranslator(data_dir='data')

def parse_metar(metar):
    """
    解析 METAR 报文，返回可读的天气报告。
    """
    # 去除首尾空格，并将多个空格合并为一个
    metar = re.sub(r'\s+', ' ', metar.strip())
    parts = metar.split()

    # 结果字典
    result = {
        'type': '',
        'airport_code': '',
        'airport_description': '',
        'time': '',
        'auto': False,
        'auto_str': '',
        'nil': False,
        'nil_str': '',
        'wind_direction': '',
        'wind_speed': '',
        'wind_gust': '',
        'wind_change': '',
        'visibility': '',
        'cavok': False,
        'rvr': [],
        'weather': [],
        'clouds': [],
        'vertical_visibility': '',
        'temperature': '',
        'dew_point': '',
        'pressure': '',
        'prediction_code': '',
        'prediction_tim': '',
        'near_weather': [],
        'wind_shear': '',
        'prediction_tapy': '',
        'prediction': {},
        'remarks': '',
        'error': '',
        'terminator': False,
        'conflict': False,
        'conflicting_content': []
    }

    for j in range(len(parts)):
        part = parts[j]
        if part == '=':
            if j + 1 < len(parts):
                result['conflict'] = True
                if not result['terminator']:
                    result['terminator'] = True
                    result['conflicting_content'].append("报文终止符（=）后仍有内容")
            parts.pop(j)
        if part.endswith('='):
            if j + 1 < len(parts):
                result['conflict'] = True
                if not result['terminator']:
                    result['terminator'] = True
                    result['conflicting_content'].append("报文终止符（=）后仍有内容")
            parts[j] = part.rstrip('=')

    i = 0
    # 避免第一位是MATER
    if i < len(parts) and re.match(r'^(METAR|SPECI)$', parts[i]):
        if re.match(r'^METAR$', parts[i]):
            result['type'] = 'METAR（机场例行天气报告）'
        elif re.match(r'^SPECI$', parts[i]):
            result['type'] = 'SPECI（机场特殊天气报告）'
        i += 1

    # 机场代码 (通常第一个)
    if i < len(parts) and re.match(r'^[A-Z]{4}$', parts[i]):
        result['airport_code'] = parts[i]
        result['airport_description'] = translator.translate(parts[i])
        i += 1

    # 时间 (格式: DDHHMMZ)
    if i < len(parts) and re.match(r'\d{6}Z$', parts[i]):
        time_str = parts[i]
        day = int(time_str[0:2])
        hour = int(time_str[2:4])
        minute = int(time_str[4:6])
        result['time'] = translator.utc_to_local(result['airport_code'], day, hour, minute)
        # 转换为本地时间
        i += 1

    if i < len(parts) and (parts[i] == 'AUTO' or parts[i] == 'NIL'):
        if parts[i] == 'NIL':
            result['nil'] = True
            result['nil_str'] = '此报文为缺省报告（缺报），报文结束'
            if len(parts) > i + 1:
                result['conflict'] = True
                result['conflicting_content'].append("报文内容冲突（缺报标志与后续内容冲突）")
            # return result
        if parts[i] == 'AUTO':
            result['auto'] = True
            result['auto_str'] = '此报文为自动报文'
        i += 1
 
    # 风
    if i < len(parts):
        wind_part = parts[i]
        # 格式: 风向风速KT/公里每小时/米每秒, 可能带G阵风, 可能VRB可变风向
        wind_pattern = re.compile(
            r'^(VRB|([0-9]{3}))([0-9]{2,3})(G([0-9]{2,3}))?'
            r'(KT|MPS|KMH)?$'
        )
        match = wind_pattern.match(wind_part)
        if match:
            direction = match.group(1)
            if direction == 'VRB':
                dir_str = "风向不定"
            else:
                dir_str = f"风向 {direction}°"
            speed = match.group(3)
            gust = match.group(5)
            unit = match.group(6)
            unit_map = {'KT': '节', 'MPS': '米/秒', 'KMH': '公里/小时'}
            unit_str = unit_map.get(unit, unit)
            result['wind_direction'] = dir_str
            result['wind_speed'] = f"{speed}{unit_str}"
            if gust:
                result['wind_gust'] = f"{gust}{unit_str}"
            if i + 1 < len(parts) and re.match(r'(([0-9]{2,3})V([0-9]{2,3}))', parts[i + 1]):
                i += 1
                wind_part = parts[i]
                wind_pattern = re.compile(r'^(([0-9]{2,3})V([0-9]{2,3}))')
                match = wind_pattern.match(wind_part)
                dir_str_change_1 = match.group(2)
                dir_str_change_2 = match.group(3)
                result['wind_change'] = f"风向在{dir_str_change_1}°到{dir_str_change_2}°之间变化"
            i += 1

    # 能见度 (可能包含CAVOK)
    if i < len(parts):
        vis_part = parts[i]
        if vis_part == 'CAVOK':
            result['visibility'] = "CAVOK (能见度≥10公里，无云，无重要天气)"
            result['cavok'] = True
            i += 1
        elif re.match(r'^[0-9]{4}$', vis_part):
            vis_m = int(vis_part)
            if vis_m >= 1000:
                result['visibility'] = f"≥{vis_m/1000:.1f} 公里"
            else:
                result['visibility'] = f"≥{vis_m} 米"
            i += 1

    # 跑道视程 (RVR)，格式: R24/1000FT 或 R24/1000V1500FT
    def RVR_PorM_parse(code, rvr):
        if code == "M":
            if not rvr == "0050":
                result['conflict'] = True
                result['conflicting_content'].append(f"跑道{rwy}视程内容冲突（M表示视程小于50米，视程应写为0050，但当前视程写为{rvr}米）")
            rvr_str = "小于50"
        elif code == "P":
            if not rvr == "2000":
                result['conflict'] = True
                result['conflicting_content'].append(f"跑道{rwy}视程内容冲突（P表示视程大于2000米，视程应写为2000，但当前视程写为{rvr}米）")
            rvr_str = "大于2000"
        return rvr_str
    while i < len(parts):
        rvr_part = parts[i]
        rvr_pattern = re.compile(r'^R([0-9]{2})(L|C|R)?/(P|M)?([0-9]{4})(V(P|M)?([0-9]{4}))?(U|D|N)?$')
        match = rvr_pattern.match(rvr_part)
        if match:
            rwy = match.group(1)
            rwy_code = match.group(2)
            if rwy_code:
                if rwy_code == 'L':
                    rwy += "左"
                elif rwy_code == 'C':
                    rwy += "中"
                elif rwy_code == 'R':
                    rwy += "右"
            low_code = match.group(3)
            low = match.group(4)
            if low_code:
                low_str = RVR_PorM_parse(low_code, low)
            else:
                low_str = low.lstrip('0')

            high_code = match.group(6)
            high = match.group(7)
            if match.group(5):
                if high_code:
                    high_str = RVR_PorM_parse(high_code, high)
                else:
                    high_str = high.lstrip('0')
            unit = match.group(8) or ''
            if match.group(5):
                result['rvr'].append(f"跑道{rwy}视程: 在{low_str}米到{high_str}米之间变化")
            else:
                result['rvr'].append(f"跑道{rwy}视程: {low_str}米")
            i += 1
        else:
            break

    # 天气现象 (可能多个)
    important_weather_map = [
        "DZ", "BR", "PO", "RA", "FG", "SQ", "SN",
        "FU", "SG", "VA", "FC", "IC", "DU",
        "PL", "SA", "SS", "GR", "HZ", "DS", "GS"
    ]
    while i < len(parts):
        weat = parts[i]
        # 检查是否包含天气代码（通常是由字母和+-组成）
        if re.match(r'^[-+]?[A-Z]{2,}$', weat) and not weat == "NSC":
            result['weather'].append(translate_weather_code(weat))
            weather_check = weat[2:]
            if any(keyword in weather_check for keyword in important_weather_map) and result['cavok'] == True:
                result['conflict'] = True
                result['conflicting_content'].append("报文内容冲突（CAVOK与天气现象冲突）")
            
            i += 1
        else:
            break

    # 云层 (可能多个)
    cloud_cover_map = {'SKC':'无云', 'FEW':'有1-2个量', 'SCT':'有3-4个量', 'BKN':'有5-6个量', 'OVC':'有7-8个量'}
    cloud_type_map = {'':'云', '///':'云', 'TCU':'浓积云', 'CB':'积雨云'}
    while i < len(parts):
        cloud_type = ""
        cloud = parts[i]
        # 云层格式: 三字母+高度（百英尺）或 特殊码如 NSC
        if cloud in ['NSC']:#, 'NCD', 'SKC', 'CLR'
            result['clouds'].append("5000英尺以下无云")
            i += 1
        elif re.match(r'^(SKC|FEW|SCT|BKN|OVC)([0-9]{3})(///|TCU|CB)?$', cloud):
            match = re.match(r'^(SKC|FEW|SCT|BKN|OVC)([0-9]{3})(///|TCU|CB)?$', cloud)
            cloud_cover = match.group(1)
            height_ft = int(match.group(2)) * 100
            if re.match(r'^(SKC|FEW|SCT|BKN|OVC)([0-9]{3})(///|TCU|CB)$', cloud):
                cloud_type = match.group(3)
            if (int(match.group(2)) <= 49 or match.group(3) in ['TCU', 'CB']) and result['cavok'] == True:
                result['conflict'] = True
                result['conflicting_content'].append("报文内容冲突（CAVOK与云层冲突）")
            result['clouds'].append(f"{height_ft}英尺{cloud_cover_map[cloud_cover]}{cloud_type_map[cloud_type]}")
            i += 1
        else:
            break

    #垂直能见度(格式: VV/// 或 VVnnn)
    if i < len(parts):
        vertical_visibility = parts[i]
        if re.match(r'^VV(///|([0-9]{3}))$', vertical_visibility):
            match = re.match(r'^VV(///|([0-9]{3}))$', vertical_visibility)
            if match.group(1) == '///':
                result['vertical_visibility'] = "无垂直能见度"
            else:
                result['vertical_visibility'] = f"≥{match.group(2)} 米"
            i += 1

    # 温度和露点 (格式: TT/DD)
    if i < len(parts):
        temp_part = parts[i]
        if re.match(r'^(M)?([0-9]{2})/(M)?([0-9]{2})', temp_part):
            match = re.match(r'^(M)?([0-9]{2})/(M)?([0-9]{2})', temp_part)
            # 处理可能带M表示负值
            def parse_temp(m, s):
                s = s.lstrip('0')
                if not s:
                    s = '0'
                if m == 'M':
                    return '-' + s if not s == '0' else '0'
                else:
                    return s
            temp = parse_temp(match.group(1), match.group(2))
            dew = parse_temp(match.group(3), match.group(4))
            result['temperature'] = f"{temp}°C"
            result['dew_point'] = f"{dew}°C"
            i += 1

    # 气压
    if i < len(parts):
        pres_part = parts[i]
        if re.match(r'^[Q|A][0-9]{3}$', pres_part):
            match = re.match(r'^[Q|A][0-9]{3}$', pres_part)
            if match.group(1) == 'Q':
                # QNH 百帕
                pres = pres_part[1:]
                result['pressure'] = f"{pres} hPa"
                i += 1
            elif match.group(1) == 'A':
                # 英寸汞柱
                pres = pres_part[1:]
                result['pressure'] = f"{pres[:2]}.{pres[2:]} 英寸汞柱"
                i += 1

    # 近时天气（可能多个）
    while i < len(parts):
        weat = parts[i]
        # 检查是否包含天气代码（通常是由字母和+-组成）
        if re.match(r'^RE[A-Z]{2,}$', weat) and not weat == "NSC":
            result['near_weather'].append(translate_weather_code(weat))
            i += 1
        else:
            break
    
    # 风切变
    if i < len(parts) and parts[i] == "WS":
        while i < len(parts):
            wind_shear = parts[i]
            if re.match(r'^R([0-9]{2}(L|C|R)?)$', wind_shear):
                match = re.match(r'^R([0-9]{2}(L|C|R)?)$', wind_shear)
                rwy = match.group(1)
                if re.match(r'^R([0-9]{2}(L|C|R))$', wind_shear):
                    if re.match(r'^R([0-9]{2}L)$', wind_shear):
                        rwy += "左"
                    elif re.match(r'^R([0-9]{2}C)$', wind_shear):
                        rwy += "中"
                    elif re.match(r'^R([0-9]{2}R)$', wind_shear):
                        rwy += "右"
                result['wind_shear'] = f"{rwy}有风切变"
                i += 1
            elif parts[i] == "ALL" and parts[i + 1] == "RWY":
                result['wind_shear'] = "所有跑道有风切变"
                i += 2
                break

    # 预报
    prediction_tapy = ""
    prediction_str = {}
    if i < len(parts):
        prediction = parts[i]
        if  re.match(r'^(NOSIG|BECMG|TEMPO)$', prediction):
            if  re.match(r'^(NOSIG)$', prediction):
                prediction_tapy += "未来两小时内，天气没有变化\n" 
            elif  re.match(r'^(BECMG)$', prediction) and re.match(r'^(FM|TL|AT)([0-9]{4})$', parts[i + 1]):
                if re.match(r'^FM([0-9]{4})$', parts[i + 1]):
                    BECMG_code = "从"
                elif re.match(r'^TL([0-9]{4})$', parts[i + 1]):
                    BECMG_code = "至"
                elif re.match(r'^AT([0-9]{4})$', parts[i + 1]):
                    BECMG_code = "在"
                BECMG = parts[i + 1]
                prediction_hour = int(BECMG[2:4])
                prediction_minute = int(BECMG[4:6])
                prediction_tim = f"{BECMG_code}\n{translator.utc_to_local(result['airport_code'], day, prediction_hour, prediction_minute)}"
                prediction_tapy += f"未来两小时内，{prediction_tim}，天气将逐渐变为:\n"
                prediction_str = parse_metar(' '.join(parts[i + 2:]))
            elif  re.match(r'^(TEMPO)$', prediction):
                prediction_tapy += "未来两小时将有临时天气\n"
                prediction_str = parse_metar(' '.join(parts[i + 1:]))
            i = len(parts)
    result['prediction_tapy'] = prediction_tapy
    result['prediction'] = prediction_str

    # 剩余部分作为备注
    if i < len(parts) and parts[i] == "RMK":
        result['remarks'] = ' '.join(parts[i + 1:])
    else:
        result['error'] = ' '.join(parts[i:])

    return result

def translate_weather_code(code):
    """将天气代码翻译成中文"""
    code_describer_map = { 
        'MI': '浅', 'BC': '散片状', 'PR': '部分', 'DR': '低吹', 'BL': '高吹','SH': '阵', 'TS': '雷暴', 'FZ': '冻',
        'RE': '近时'
    }
    code_map = {  
        'DZ': '毛毛雨', 'BR': '轻雾', 'PO': '尘/沙旋风（尘卷风）', 'RA': '雨', 'FG': '雾', 'SQ': '飑', 'SN': '雪',
        'FU': '烟', 'SG': '米雪', 'VA': '火山灰', 'FC': '龙卷云（陆龙卷/水龙卷）', 'IC': '冰晶/冰针', 'DU': '浮尘',
        'PL': '冰粒', 'SA': '沙', 'SS': '沙暴', 'GR': '冰雹', 'HZ': '霾', 'DS': '尘暴', 'GS': '小冰雹或霰',
        'FR':'霜', 'RI':'雾凇', 'PS':'积雪', 'VG':'雨淞', 'GA':'大风', 'WS':'风切变', 'TS': '雷暴', 'UP': '未知天气',
        'FZUP': '冻未知天气'
    }
    translated = ''
        
    if code == 'NSW':
        translated += '无显著天气'
        #NSW可能代表无天气

    # 处理 + 和 -
    # intensity = ''
    if code.startswith('+'):
        translated += '强'
        # intensity = '强'
        code = code[1:]
    elif code.startswith('-'):
        translated += '弱'
        # intensity = '弱'
        code = code[1:]
    elif code.startswith('VC'):
        translated += '附近有'
        code = code[2:]
    # 处理描述符和现象

    # 常见两字母现象
    if code in code_map:
        translated += code_map[code]
    else:
        # 可能有多字母，尝试拆分
        # 粗略处理
        if len(code) >= 4:
            describer = code[:2]
            code1 = code[2:]
            if describer in code_describer_map:
                translated += code_describer_map[describer]
            else:
                    translated += describer
            if code1 in code_map:
                translated += code_map[code1]
            else:
                code2 = code1[:2]
                code3 = code1[2:]
                if code2 in code_map and code3 in code_map:
                    translated += f"{code_map[code2]}夹{code_map[code3]}"
                else:
                    translated += code1
        else:
            translated += code
    return translated

def translate_codes(parsed):
    result = ""
    if parsed['type']:
        result += f"报文类型：{parsed['type']}\n"
    if parsed['airport_code']:
        result += f"机场代码：{parsed['airport_code']}\n"
    if parsed['airport_description']:
        result += parsed['airport_description'] + "\n"
    if parsed['time']:
        result += f"\n观测时间：{parsed['time']}\n"
    if parsed['auto']:
        result += parsed['auto_str'] + "\n"
    if parsed['nil']:
        result += parsed['nil_str'] + "\n"
    if parsed['wind_direction']:
        result += f"风：\n    风向：{parsed['wind_direction']}\n    风速：{parsed['wind_speed']}\n"
        if parsed['wind_gust']:
            result += f"    阵风 {parsed['wind_gust']}\n"
        if parsed['wind_change']:
            result += f"    风向变化：{parsed['wind_change']}\n"
    if parsed['visibility']:
        result += f"能见度：{parsed['visibility']}\n"
    if parsed['rvr']:
        result += f"跑道视程：\n    "
        result += '\n    '.join(parsed['rvr'])
        result += '\n'
    if parsed['weather']:
        result += f"天气现象：\n    "
        result += '\n    '.join(parsed['weather'])
        result += '\n'
    if parsed['clouds']:   # NSC, NCD, SKC, CLR
        result += f"云层：\n    "
        result += '\n    '.join(parsed['clouds'])
        result += '\n'
    if parsed['vertical_visibility']:
        result += f"垂直能见度：{parsed['vertical_visibility']}\n"
    if parsed['temperature']:
        result += f"温度：{parsed['temperature']}\n"
    if parsed['dew_point']:
        result += f"露点：{parsed['dew_point']}\n"
    if parsed['pressure']:
        result += f"气压：{parsed['pressure']}\n"
    if parsed['near_weather']:
        result += f"近时天气：\n    "
        result += '\n    '.join(parsed['near_weather'])
        result += '\n'
    if parsed['wind_shear']:
        result += f"风切变：{parsed['wind_shear']}\n"
    if parsed['prediction_tapy']:
        result += "\n" + parsed['prediction_tapy']
    if parsed['prediction']:
        result += translate_codes(parsed['prediction'])
    if parsed['remarks']:
        result += f"\n备注：{parsed['remarks']}\n"
    if parsed['error']:
        result += f"\n无法翻译部分：{parsed['error']}\n"
    if parsed['conflict']:
        result += f"\n⚠️警告：报文内容冲突（{'; '.join(parsed['conflicting_content'])}）\n"
    return result
    

def main():
    print("-" * 60)
    print("报文翻译程序")
    print("ICAO机场代码相关功能基于 mwgg_airports 数据库，国家代码翻译功能相关数据由 IP2Location 提供")
    print("mwgg_airports：https://github.com/mwgg/Airports")
    print("IP2Location：https://www.ip2location.com/free/country-multilingual")
    print("请确保 airports.json 文件位于程序同目录下")
    print("-" * 60)
    print("请输入 METAR 报文（例如：ZSSS 251200Z 12005KT 9999 FEW020 18/12 Q1018 NOSIG）")
    metar = input("\nMETAR: ").strip()

    # 测试用
    # metar = "SPECI ZGGG 011348Z VRB01MPS 5000 +TSRA SCT033CB  BKN050 25/16 Q1013 BECMG AT1420 -TSRA"
    # metar = "METAR ZBAA 110800Z 15006MPS 110V190 CAVOK R12L/0200 R13C/P2000 R14R/P2000VM0150 M20/M00 Q1010 NOSIG"

    if metar.lower() in ('quit', 'exit', 'q'):
        return
    while not metar:
        metar = input("\n请输入 正确的METAR 报文：").strip()
    parsed = parse_metar(metar)
    print("\n翻译结果：")
    print(translate_codes(parsed))

if __name__ == '__main__':
    main()