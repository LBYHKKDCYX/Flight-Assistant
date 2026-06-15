# 航空助手 ✈️

一个基于 Flask + Vue 3 的航空信息查询工具，提供 ICAO 机场代码查询和 METAR 气象报文翻译功能。

## ⚠️ **免责声明：**  

- 本项目**仅供虚拟飞行和业余爱好者使用**.  
- **切勿将此或其提供的任何信息用于真实飞行**

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

- **截图分享**：查询结果一键生成为图片并复制到剪贴板

- **历史记录**：自动保存最近查询的 ICAO 代码，点击快速回查

## 技术栈

- **后端**：Python + Flask（纯 API 服务）
- **前端**：Vue 3 + Vite
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
pip install -r backend/requirements.txt
```

Vue 前端首次需安装：

```bash
cd frontend
npm install
```

### 数据准备

- 从 [mwgg/Airports](https://github.com/mwgg/Airports) 下载 `airports.json`，放在 `backend/data/` 目录下
- 从 [IP2Location](https://www.ip2location.com/free/country-multilingual) 下载 `country_multilingual.csv`（重命名为 `country_translations.csv`），放在 `backend/data/` 目录下

- `timezone_translations.json` — 项目自带，无需额外下载

### 启动

```bash
python run_dev.py
```

自动启动 Flask 后端（`localhost:5000`）+ Vue 开发服务器（`localhost:5173`），并打开浏览器。

**手动启动：**

```bash
# 终端 1 — Flask 后端
cd backend
python app.py

# 终端 2 — Vue
cd frontend
npx vite --host
```

## 示例

### ICAO 代码查询

输入：`ZBAA`

输出：
```
机场名称：Beijing Capital International Airport
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
├── backend/                       # Flask 后端
│   ├── translator/                # 翻译核心模块
│   │   ├── __init__.py            # 统一导出
│   │   ├── icao.py                # ICAO 翻译器
│   │   └── metar.py               # METAR 报文解析
│   ├── data/                      # 静态数据（需下载）
│   │   ├── airports.json
│   │   ├── country_translations.csv
│   │   └── timezone_translations.json
│   ├── utils.py                   # 外部 API 调用
│   ├── app.py                     # Flask 路由定义
│   ├── run.py                     # 启动入口
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                      # Vue 3 前端
│   ├── public/                    # favicon 等静态资源
│   ├── src/
│   │   ├── components/
│   │   │   ├── IcaoQuery.vue      # ICAO 查询卡片
│   │   │   ├── MetarTranslate.vue # METAR 翻译卡片
│   │   │   ├── AeroIcon.vue       # SVG 图标组件
│   │   │   └── ToastContainer.vue # Toast 提示
│   │   ├── composables/
│   │   │   ├── useToast.js        # 响应式提示
│   │   │   ├── useHistory.js      # 历史记录
│   │   │   └── useShare.js        # 截图分享
│   │   ├── App.vue                # 根组件
│   │   ├── main.js                # Vue 入口
│   │   └── style.css              # 全局样式
│   ├── index.html                 # Vite 入口 HTML
│   ├── package.json
│   └── vite.config.js             # API 代理配置
│
├── run_dev.py                     # 一键启动（Flask + Vue）
├── .gitignore
└── README.md
```

## API 接口

### 前端专用 API
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api_web/icao` | ICAO 机场查询 |
| POST | `/api_web/metar` | METAR 报文翻译 |
| POST | `/api_web/fetch_metar` | 通过 ICAO 获取实时 METAR |

### 通用 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/icao/<icao>?format=dict\|string` | 查询 ICAO 机场 |
| POST | `/api/v1/metar/translate?format=dict\|string` | 翻译 METAR 报文 |
| GET | `/api/v1/metar/fetch/<icao>?raw&translated&format` | 获取并翻译实时 METAR |

### Swagger 文档

```
http://localhost:5000/apidocs
```

## 注意事项

1. **数据文件**：`airports.json` 和 `country_translations.csv` 需自行下载到 `backend/data/`
2. **网络依赖**：获取实时 METAR 需要网络连接
3. **时区**：Python 3.9+ 使用内置 zoneinfo，3.9 以下需 `pip install pytz`
4. **首次运行**：`frontend/node_modules/` 目录不存在时会自动执行 `npm install`

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 致谢

- 机场数据：[mwgg/Airports](https://github.com/mwgg/Airports)
- 国家代码翻译：[IP2Location](https://www.ip2location.com/free/country-multilingual)
- METAR 实时数据：[isfpapi.flyisfp.com](https://isfpapi.flyisfp.com/api/metar)
- API 文档：[Flasgger](https://github.com/flasgger/flasgger)
- 截图功能：[html2canvas](https://html2canvas.hertzen.com/)

---

Enjoy your flight! ✈️
