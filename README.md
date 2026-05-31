# 航空助手 ✈️

一个基于 Flask + Vue 3 的航空信息查询工具，提供 ICAO 机场代码查询和 METAR 气象报文翻译功能。

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
  - 详细的天气信息解析（风向风速、能见度、天气现象、云层、温度露点、气压、风切变等）
  - 自动时区转换，显示当地时间
  - 报文终止符（=）自动处理与冲突检测

- **截图分享**：支持将查询结果一键生成为图片并复制到剪贴板

- **历史记录**：自动保存最近查询的 ICAO 代码，点击即可快速回查

## 技术栈

- **后端**：Python + Flask
- **前端**：Vue 3 + Vite（开发） / 原生 HTML + CSS + JS（Flask 模板）
- **API 文档**：Flasgger (Swagger UI)
- **截图**：html2canvas (v1.4.1)
- **数据来源**：
  - 机场数据：[mwgg/Airports](https://github.com/mwgg/Airports) (airports.json，约 29,000 个机场)
  - 国家代码翻译：[IP2Location 国家代码数据库](https://www.ip2location.com/free/country-multilingual) (country_translations.csv，249 个国家/地区)
  - METAR 实时数据：[isfpapi.flyisfp.com](https://isfpapi.flyisfp.com/api/metar)
  - 时区翻译：内置 IANA 时区中文映射表 (timezone_translations.json)

## 安装与运行

### 前提条件

- Python 3.7+
- Node.js 18+（仅 Vue 前端需要）
- pip 包管理工具

### 安装依赖

```bash
pip install -r requirements.txt
```

Vue 前端首次使用需安装：

```bash
cd frontend
npm install
```

### 数据准备

- 从 [mwgg/Airports](https://github.com/mwgg/Airports) 下载 `airports.json`，放在 `data/` 目录下
- 从 [IP2Location](https://www.ip2location.com/free/country-multilingual) 下载 `country_multilingual.csv`（重命名为 `country_translations.csv`），放在 `data/` 目录下

### 启动项目

**一键启动（推荐）：**

```bash
python run_dev.py
```

自动启动 Flask 后端（`localhost:5000`）+ Vue 开发服务器（`localhost:5173`），并打开浏览器。

**手动启动：**

```bash
# 终端 1 — Flask 后端
python app.py                          # → localhost:5000

# 终端 2 — Vue 前端
cd frontend && npx vite --host         # → localhost:5173
```

**仅用 Flask 模板版（不需要 Node.js）：**

```bash
python app.py                          # → localhost:5000
```

## 示例

### ICAO 代码查询

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

### METAR 报文翻译

输入：`ZSSS 251200Z 12005KT 9999 FEW020 18/12 Q1018 NOSIG`

输出：
```
报文类型：METAR（机场例行天气报告）
机场代码：ZSSS
...
风：
    风向：120°
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
├── data/                         # 数据文件（需自行下载）
│   ├── airports.json             # 机场数据库（约 29,000 条）
│   ├── country_translations.csv  # 国家代码翻译（249 条）
│   └── timezone_translations.json # 时区中文翻译表
├── static/
│   ├── css/style.css             # Flask 模板样式
│   ├── favicon.ico
│   ├── favicon-16x16.png
│   └── favicon-32x32.png
├── templates/
│   └── index.html                # Flask 模板版前端（原生 JS）
├── frontend/                     # Vue 3 前端项目
│   ├── public/                   # 静态资源
│   ├── src/
│   │   ├── components/
│   │   │   ├── IcaoQuery.vue     # ICAO 查询卡片
│   │   │   ├── MetarTranslate.vue # METAR 翻译卡片
│   │   │   ├── AboutSection.vue  # 关于卡片
│   │   │   └── ToastContainer.vue # Toast 提示
│   │   ├── composables/
│   │   │   ├── useToast.js       # 响应式提示
│   │   │   ├── useHistory.js     # 历史记录
│   │   │   └── useShare.js       # 截图分享
│   │   ├── App.vue               # 根组件
│   │   ├── main.js               # Vue 入口
│   │   └── style.css             # 全局样式
│   ├── index.html                # Vue 入口 HTML
│   ├── package.json              # Node 依赖
│   └── vite.config.js            # Vite 配置（API 代理）
├── app.py                        # Flask 应用主入口
├── api.py                        # 外部 METAR API 调用
├── ICAO_code_translate.py        # ICAO 翻译器
├── METAR_translate.py            # METAR 报文解析器
├── run_dev.py                    # 一键启动脚本
├── requirements.txt
├── .gitignore
└── README.md
```

## API 接口

### 前端专用 API（返回格式化字符串）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api_web/icao` | ICAO 机场查询 |
| POST | `/api_web/metar` | METAR 报文翻译 |
| POST | `/api_web/fetch_metar` | 通过 ICAO 获取实时 METAR |

### 通用 API（返回 JSON）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/icao/<icao>?format=dict\|string` | 查询 ICAO 机场信息 |
| POST | `/api/v1/metar/translate?format=dict\|string` | 翻译 METAR 报文 |
| GET | `/api/v1/metar/fetch/<icao>?raw&translated&format` | 获取并翻译实时 METAR |

### Swagger 文档

启动后访问 `http://localhost:5000/apidocs`

## 注意事项

1. **数据更新**：airports.json 和 country_translations.csv 需自行下载，放在 `data/` 目录下
2. **网络依赖**：获取实时 METAR 报文需要网络连接
3. **时区支持**：Python 3.9+ 使用内置 zoneinfo，3.9 以下需 `pip install pytz`
4. **Vue 开发**：需要 Node.js 环境，但 Flask 模板版可直接使用无需额外安装

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
