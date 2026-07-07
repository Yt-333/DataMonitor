# NebulaScreen 星云大屏

企业级数据可视化驾驶舱。当前阶段纯前端运行、完全使用 Mock 数据；未来可零改动切换真实 API。

## 技术栈
Vue 3 + TypeScript(strict) + Vite · Pinia · ECharts 5 + vue-echarts · SCSS · Vitest · ESLint + Prettier

## 快速开始
```bash
npm install
npm run dev      # http://localhost:5173
npm run test     # 运行 Vitest
npm run build    # 类型检查 + 生产打包
```

## 架构

```
src/
├── api/
│   ├── types.ts              # 业务数据类型 + DataService 接口
│   ├── mock/
│   │   ├── mockData.ts       # 纯数据生成函数（±5% 随机波动）
│   │   └── mockService.ts    # DataService 实现：300~800ms 延迟 + 5% 失败
│   └── service/
│       ├── DataService.ts    # 接口再导出
│       └── apiService.ts     # 真实 API 实现（暂抛错，预留请求注释）
├── components/
│   ├── common/               # BorderBox / DigitalFlop / Loading / AlarmScroll
│   └── charts/               # BaseChart + Line/Bar/Pie/Radar
├── composables/              # useScreenAdapt / useDataService / usePolling
├── stores/screenStore.ts     # Pinia 全局业务状态
├── logger/logger.ts          # 统一日志
├── views/MainScreen.vue      # 主大屏
├── App.vue
└── main.ts                   # 数据源注入 + 全局错误处理
```

## Mock / API 切换

数据来源由环境变量 `VITE_DATA_SOURCE` 决定，在 `main.ts` 中据此实例化服务，并通过 `provide/inject` 注入全局。组件与 Store 只依赖 `DataService` 抽象接口，**完全不知道数据来源**。

```bash
# .env
VITE_DATA_SOURCE=mock   # 默认：本地 Mock
VITE_DATA_SOURCE=api    # 切换真实后端
```

切换到真实 API 时：把 `src/api/service/apiService.ts` 中每个方法的 `throw` 替换为已预留的 `fetch` 请求即可，业务组件零改动。
