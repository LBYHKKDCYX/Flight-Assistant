# 航空助手 ✈️

一个基于 Flask 的航空信息查询工具，提供 ICAO 机场代码查询和 METAR 气象报文翻译功能。

## 功能特点

- **ICAO 机场代码查询**：输入 4 字母 ICAO 代码，获取机场详细信息
  - 机场名称、IATA 代码
  - 所在城市、国家
  - 海拔高度（英尺/米）
  - 经纬度（十进制度/度分秒格式）
  - 时区信息（含 UTC 偏移）

- **METAR 气象报文翻译**：
  - 支持手动输入 METAR 报文进行翻译
  - 支持通过 ICAO 代码获取实时 METAR 报文并自动翻译
  - 详细的天气信息解析（风向风速、能见度、天气现象、云层、温度露点、气压等）
  - 自动时区转换，显示当地时间

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML5 + CSS3 + JavaScript
- **数据来源**：
  - 机场数据：[mwgg/Airports](https://github.com/mwgg/Airports) (airports.json)
  - 国家代码翻译：IP2Location 国家代码数据库
  - METAR 实时数据：[isfpapi.flyisfp.com](https://isfpapi.flyisfp.com/api/metar)

## 安装与运行

### 前提条件

- Python 3.7 或更高版本
- pip 包管理工具

### 安装步骤

1. **克隆或下载项目到本地**

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

   如果没有 requirements.txt 文件，请手动安装以下依赖：
   ```bash
   pip install flask requests
   ```

   对于 Python 3.9 以下版本，还需要安装时区库：
   ```bash
   pip install pytz
   ```

3. **下载必要的数据文件**
   - 从 [mwgg/Airports](https://github.com/mwgg/Airports) 下载 `airports.json` 文件，放在项目根目录
   - 确保 `country_multilingual.csv` 文件存在于项目根目录（用于国家代码翻译）

### 运行项目

在项目根目录执行：

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

## 使用说明

### ICAO 机场代码查询
1. 在 "ICAO 代码查询" 卡片中输入 4 字母的 ICAO 代码（如 ZBAA、KJFK、EGLL）
2. 点击 "查询机场信息" 按钮或按下回车键
3. 系统将显示该机场的详细信息

### METAR 气象报文翻译

#### 方法一：手动输入 METAR 报文
1. 在 "METAR 报文翻译" 卡片的文本框中输入 METAR 报文
2. 点击 "翻译报文" 按钮或按下 Ctrl+Enter
3. 系统将解析并翻译该报文

#### 方法二：获取实时 METAR 报文
1. 在 "或通过 ICAO 获取实时报文" 输入框中输入机场 ICAO 代码
2. 点击 "获取实时报文" 按钮
3. 系统将自动获取并填充最新的 METAR 报文，然后自动翻译

## 示例

### ICAO 代码查询示例

输入：`ZBAA`

输出：
```
机场名称：北京首都国际机场
IATA代码：PEK
所在城市：北京
所在国家：中国
海拔：56英尺，17米
纬度：40.079997999999994（40°4′48.00″N）
经度：116.603333（116°36′12.00″E）
时区：中国标准时间 (北京) (UTC+8)
```

### METAR 报文翻译示例

输入：`ZSSS 251200Z 12005KT 9999 FEW020 18/12 Q1018 NOSIG`

输出：
```
报文类型：METAR（机场例行天气报告）
机场代码：ZSSS
机场名称：上海虹桥国际机场
IATA代码：SHA
所在城市：上海
所在国家：中国
海拔：13英尺，4米
纬度：31.197777999999997（31°11′52.00″N）
经度：121.336944（121°20′13.00″E）
时区：中国标准时间 (上海) (UTC+8)

观测时间：UTC时间2024-03-25 12:00 UTC
对应当地时间为: 2024-03-25 20:00 CST（年月以当前UTC时间为根据）
风：风向 120°，风速 05节
能见度：≥10.0 公里
云层：2000英尺有1-2个量云
温度/露点：温度 18°C，露点 12°C
气压：1018 hPa

未来两小时内，天气没有变化
```

## 项目结构

```
航空助手/
├── __pycache__/            # Python 编译缓存
├── static/                 # 静态文件
│   ├── css/                # CSS 样式
│   └── *.png, *.ico        # 图标文件
├── templates/              # HTML 模板
│   └── index.html          # 主页面
├── ICAO_code_translate.py  # ICAO 代码翻译模块
├── METAR_translate.py      # METAR 报文翻译模块
├── api.py                  # 外部 API 调用模块
├── app.py                  # Flask 应用主文件
├── airports.json           # 机场数据库
├── country_multilingual.csv # 国家代码翻译数据库
└── README.md               # 项目说明文档
```

## 注意事项

1. **数据更新**：airports.json 文件可能需要定期更新以获取最新的机场信息
2. **网络依赖**：获取实时 METAR 报文需要网络连接
3. **时区支持**：
   - Python 3.9+ 使用内置的 zoneinfo 模块
   - Python 3.9 以下版本需要安装 pytz 库
4. **错误处理**：系统会对输入错误和网络异常进行友好提示

## 许可证

本项目仅供学习和参考使用

## 致谢

- 机场数据来自 [mwgg/Airports](https://github.com/mwgg/Airports)
- 国家代码翻译数据由 [IP2Location](https://www.ip2location.com/free/country-multilingual) 提供
- METAR 实时数据由 [isfpapi.flyisfp.com](https://isfpapi.flyisfp.com/api/metar) 提供

---

** Enjoy your flight! ✈️ **