# 航空助手 ✈️

一个基于 Flask 的航空信息查询工具，提供 ICAO 机场代码查询和 METAR 气象报文翻译功能，支持 PWA 安装到桌面。

## 功能特点

- **ICAO 机场代码查询**：输入 4 字母 ICAO 代码，获取机场详细信息
  - 机场名称、IATA 代码
  - 所在城市、国家
  - 海拔高度（英尺/米）
  - 经纬度（十进制度/度分秒格式）
  - 时区信息（含 UTC 偏移和中文时区名称）

- **METAR 气象报文翻译**：
  - 支持手动输入 METAR 报文进行翻译
  - 支持通过 ICAO 代码获取实时 METAR 报文并自动翻译
  - 详细的天气信息解析（风向风速、能见度、天气现象、云层、温度露点、气压等）
  - 自动时区转换，显示当地时间
  - 报文终止符（=）自动处理与冲突检测

- **截图分享**：支持将查询结果一键生成为图片并复制到剪贴板

- **PWA 支持**：
  - 可安装到手机或电脑桌面，像原生 App 一样使用
  - Service Worker 缓存静态资源，支持离线访问
  - 独立窗口运行，无浏览器外壳

- **历史记录**：自动保存最近查询的 ICAO 代码，点击即可快速回查

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML5 + CSS3 + JavaScript（原生，无框架）
- **API 文档**：Flasgger (Swagger UI)
- **PWA**：Web App Manifest + Service Worker (Cache API)
- **截图**：html2canvas (v1.4.1)
- **数据来源**：
  - 机场数据：[mwgg/Airports](https://github.com/mwgg/Airports) (airports.json，约 29,000 个机场)
  - 国家代码翻译：[IP2Location 国家代码数据库](https://www.ip2location.com/free/country-multilingual) (country_translations.csv，249 个国家/地区)
  - METAR 实时数据：[isfpapi.flyisfp.com](https://isfpapi.flyisfp.com/api/metar)
  - 时区翻译：内置部分 IANA 时区中文映射表 (timezone_translations.json)

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
   pip install flask requests flasgger
   ```

   对于 Python 3.9 以下版本，还需要安装时区库：
   ```bash
   pip install pytz
   ```

3. **下载必要的数据文件**
   - 从 [mwgg/Airports](https://github.com/mwgg/Airports) 下载 `airports.json` 文件，放在 `data/` 目录下
   - 从 [IP2Location](https://www.ip2location.com/free/country-multilingual) 下载 `country_multilingual.csv`截取所需部分（重命名为 `country_translations.csv`），放在 `data/` 目录下

### 运行项目

在项目根目录执行：

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

### PWA 安装

用 Chrome 打开 `http://localhost:5000`，地址栏右侧会出现安装图标，点击即可安装。手机端 Chrome 底部会弹出"添加到主屏幕"提示。详见 [site.webmanifest](static/site.webmanifest) 和 [sw.js](static/sw.js)。

## 使用说明

### ICAO 机场代码查询
1. 在 "ICAO 代码查询" 卡片中输入 4 字母的 ICAO 代码（如 ZBAA、KJFK、EGLL）
2. 点击 "查询机场信息" 按钮或按下回车键
3. 系统将显示该机场的详细信息
4. 可点击 📋 复制查询结果，或 📸 生成分享截图
5. 历史记录按钮可快速回查之前查询过的机场

### METAR 气象报文翻译

#### 方法一：手动输入 METAR 报文
1. 在 "METAR 报文翻译" 卡片的文本框中输入 METAR 报文
2. 点击 "翻译报文" 按钮或按下 Ctrl+Enter
3. 系统将解析并翻译该报文
4. 可点击 📋 复制翻译结果，或 📸 生成分享截图

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
ICAO代码：ZBAA
IATA代码：PEK
所在城市：Beijing (Beijing)
所在国家：中国
海拔：116英尺，35米
纬度：40.0801010132（40°4′48.36″N）
经度：116.5849990845（116°35′6.00″E）
时区：中国标准时间 (上海) (UTC+8)
```

### METAR 报文翻译示例

输入：`ZSSS 251200Z 12005KT 9999 FEW020 18/12 Q1018 NOSIG`

输出：
```

机场代码：ZSSS
机场名称：Shanghai Hongqiao International Airport
IATA代码：SHA
所在城市：Shanghai (Shanghai)
所在国家：中国
海拔：10英尺，3米
纬度：31.1979007721（31°11′52.44″N）
经度：121.3359985352（121°20′9.59″E）
时区：中国标准时间 (上海) (UTC+8)

观测时间：UTC时间2026-05-25 12:00 UTC
对应当地时间为: 2026-05-25 20:00 CST（年月以当前UTC时间为根据）
风：
    风向：风向 120°
    风速：05节
能见度：≥10.0 公里
云层：
    2000英尺有1-2个量云
温度：18°C
露点：12°C
气压：1018 hPa

未来两小时内，天气没有变化
```

## 项目结构

```
航空助手/
├── data/                     # 数据文件目录（需自行下载）
│   ├── airports.json         # 机场数据库（约 29,000 条）
│   ├── country_translations.csv  # 国家代码翻译（249 条）
│   └── timezone_translations.json # 时区中文翻译表
├── static/                   # 静态文件
│   ├── css/
│   │   └── style.css         # 主样式表
│   ├── sw.js                 # Service Worker（PWA 缓存）
│   ├── site.webmanifest      # PWA 清单文件
│   ├── android-chrome-192x192.png  # PWA 图标 192px
│   ├── android-chrome-512x512.png  # PWA 图标 512px
│   ├── apple-touch-icon.png  # iOS 桌面图标
│   ├── favicon.ico           # 浏览器标签页图标
│   ├── favicon-16x16.png
│   └── favicon-32x32.png
├── templates/
│   └── index.html            # 主页面（含 ICAO + METAR + About）
├── app.py                    # Flask 应用主入口（路由定义）
├── api.py                    # 外部 API 调用（获取实时 METAR）
├── ICAO_code_translate.py    # ICAO 翻译器（数据加载/时区/度分秒转换）
├── METAR_translate.py        # METAR 报文解析器（正则解析 + 中文翻译）
├── requirements.txt          # Python 依赖清单
├── .gitignore
└── README.md
```

## API 接口

### 前端专用 API（返回格式化字符串，供 Web 界面使用）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api_web/icao` | ICAO 机场查询 |
| POST | `/api_web/metar` | METAR 报文翻译 |
| POST | `/api_web/fetch_metar` | 通过 ICAO 获取实时 METAR 原始报文 |

### 通用 API（返回 JSON，可配置输出格式）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/icao/<icao>?format=dict\|string` | 查询 ICAO 机场信息 |
| POST | `/api/v1/metar/translate?format=dict\|string` | 翻译 METAR 报文 |
| GET | `/api/v1/metar/fetch/<icao>?raw&translated&format` | 获取并翻译实时 METAR |

### API 文档
项目集成了 Swagger UI，启动后访问 API 文档：
```
http://localhost:5000/apidocs
```

## 注意事项

1. **数据更新**：airports.json 和 country_translations.csv 需自行下载，放在 `data/` 目录下
2. **网络依赖**：获取实时 METAR 报文需要网络连接
3. **时区支持**：
   - Python 3.9+ 使用内置 zoneinfo 模块
   - Python 3.9 以下需要 `pip install pytz`
4. **PWA 要求**：Service Worker 仅在 HTTPS 或 localhost 下生效
5. **截图分享**：依赖 html2canvas（CDN 加载），需网络连接

## 许可证

本项目仅供学习和参考使用

## 致谢

- 机场数据：[mwgg/Airports](https://github.com/mwgg/Airports)
- 国家代码翻译：[IP2Location](https://www.ip2location.com/free/country-multilingual)
- METAR 实时数据：[isfpapi.flyisfp.com](https://isfpapi.flyisfp.com/api/metar)
- API 文档：[Flasgger](https://github.com/flasgger/flasgger)
- 截图功能：[html2canvas](https://html2canvas.hertzen.com/)

---

Enjoy your flight! ✈️
