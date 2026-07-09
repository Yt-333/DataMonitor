# NebulaScreen 星云数据驾驶舱
<img width="3071" height="1676" alt="4dda6d29dc6bd3c52caee9e4349f86c7" src="https://github.com/user-attachments/assets/4cb627fd-3905-4978-9b4b-0833f87295dc" />

数据中心运行监控大屏 —— 基于 bigdata 四张明细表（主机、指标字典、磁盘监控、性能监控）构建的全栈数据可视化平台。

## 项目结构

```
nebula-screen/
├── bigdata/                    # 原始数据 + 加工结果
│   ├── host_detail.dat         #   20 台主机信息
│   ├── mod_detail.dat          #   55 个指标字典
│   ├── disk_tsar.dat           #   12,000 条磁盘监控
│   ├── pref_tsar.dat           #   67,200 条性能监控
│   └── outputs/                #   数据清洗 + 核心结果表（小时级聚合）
│       ├── 数据清洗/
│       │   └── tsar_cleaned_with_datetime.csv
│       ├── 核心结果表/
│       │   ├── hourly_stats_by_metric.csv
│       │   └── hourly_stats_by_host_mod.csv
│       └── 可视化图表/
├── backend/                    # Python FastAPI 后端
│   ├── main.py                 #   API 服务 (port 8000)
│   ├── etl_load.py             #   ETL 脚本 (bigdata → MySQL)
│   ├── requirements.txt        #   Python 依赖
│   └── Dockerfile              #   后端容器
├── db/init/
│   └── 01-schema.sql           # MySQL 建表脚本 (8 tables + views)
├── src/                        # Vue 3 前端
│   ├── main.ts                 #   入口 (auto-detect API/mock)
│   ├── App.vue                 #   根组件
│   ├── views/
│   │   └── MainScreen.vue      #   ★ 主大屏视图 (PC + 移动端响应式)
│   ├── stores/
│   │   └── screenStore.ts      #   Pinia 状态管理
│   ├── composables/
│   │   ├── useScreenAdapt.ts   #   屏幕缩放 + 移动端检测
│   │   ├── usePolling.ts       #   定时轮询
│   │   └── useDataService.ts   #   DI 注入
│   ├── api/
│   │   ├── types.ts            #   TypeScript 类型定义
│   │   ├── mock/               #   Mock 数据源
│   │   └── service/            #   真实 API 数据源
│   ├── components/
│   │   ├── common/             #   BorderBox, DigitalFlop, AlarmScroll, Loading
│   │   └── charts/             #   LineChart, BarChart, PieChart, RadarChart
│   └── styles/                 #   SCSS tokens + global styles
├── docker-compose.yml          # 一键启动 MySQL + API + Nginx
├── nginx.conf                  # Nginx 反向代理配置
├── vite.config.ts              # Vite 配置 (含 /api 代理)
└── .env                        # 环境变量
```

## 快速启动

### 1. 环境要求

| 组件 | 版本 |
|------|------|
| Node.js | ≥ 20.x |
| Python | ≥ 3.11 |
| Docker & Docker Compose | 最新版 |
| MySQL | 8.0 (Docker 提供) |

### 2. 启动 MySQL + 后端 API

```bash
# 启动 MySQL（首次启动会自动运行 db/init/01-schema.sql 建表）
docker compose up mysql -d

# 等待 MySQL 就绪后，运行 ETL 导入数据
pip install pymysql pandas sqlalchemy --break-system-packages
python backend/etl_load.py

# 启动后端 API
pip install fastapi uvicorn --break-system-packages
python backend/main.py
# 或者用 Docker:
# docker compose up api -d
```

### 3. 启动前端开发服务器

```bash
npm install
npm run dev
```

浏览器打开 `http://localhost:5173` 查看大屏。

前端会自动检测后端是否可用：
- 如果 API 健康检查通过 → 使用真实数据
- 如果 API 不可达 → 自动降级到 Mock 数据

### 4. 一键生产部署

```bash
# 构建前端
npm run build

# 启动全部服务 (MySQL + API + Nginx 静态服务)
docker compose up -d
```

浏览器打开 `http://localhost:8080`。

### 5. 移动端大屏

同一套代码已内置响应式适配。在手机/平板浏览器直接打开即可自动切换为移动端布局（竖屏堆叠 KPI 卡片 + 图表，横屏保留横向排列）。

## 数据流

```
bigdata/*.dat  ──►  ETL (pandas)  ──►  MySQL (nebula_screen)
                                            │
                               FastAPI (:8000)   ◄── 每小时聚合 + 告警生成
                                    │
                               /api/metrics
                               /api/trend
                               /api/alarms
                               /api/charts
                                    │
                              Vue 3 前端 (:5173)  ──►  浏览器大屏
                                    │
                     (健康检查失败时自动降级)
                                    │
                              MockService (本地随机数据)
```

## MySQL 数据库表

| 表名 | 行数 | 说明 |
|------|------|------|
| `host_detail` | 20 | 主机信息 |
| `mod_detail` | 55 | 指标字典 |
| `tsar_raw` | ~79,200 | 原始采集记录 |
| `metrics_snapshot` | 1 | 当前 KPI 快照 |
| `hourly_stats_by_metric` | ~55×1000 | 小时级按指标聚合 |
| `hourly_stats_by_host_mod` | ~20×55×1000 | 小时级按主机聚合 |
| `alarms` | ~10 | 告警记录 |
| `radar_scores` | 6 | 综合评分 |

## 大屏视图

### PC 端 (≥ 768px)
| 区域 | 内容 |
|------|------|
| 左侧 | 4 个数字翻牌器 KPI：设备总数、在线率、今日产量、告警数量 |
| 中央上 | 24 小时产量·效率趋势折线图 |
| 中央下左 | 告警分类占比饼图 |
| 中央下右 | 综合运行评分雷达图 |
| 右侧 | 区域生产排行条形图 |
| 底部 | 实时告警滚动列表 |

### 移动端 (< 768px)
- KPI 卡片顶部横向排列 → 竖屏单列滚动
- 趋势图 → 饼图/雷达图 → 排行 → 告警流 自上而下堆叠
- 标题和时钟字号自适应缩小

## 技术栈

| 层 | 技术 |
|----|------|
| 前端框架 | Vue 3 + TypeScript + Composition API |
| 构建工具 | Vite 6 |
| 状态管理 | Pinia |
| 图表库 | ECharts 5 (via vue-echarts) |
| 样式 | SCSS + CSS Grid (暗色主题) |
| 后端 | Python FastAPI + uvicorn |
| 数据库 | MySQL 8.0 |
| 数据处理 | pandas + SQLAlchemy |
| 容器化 | Docker + Docker Compose
