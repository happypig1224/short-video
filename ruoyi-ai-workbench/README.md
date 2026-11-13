# 若依风格 AI 可灵生图工作台 (RuoYi AI Image Workbench)

基于 **Vue 3 + Vite + Element Plus** 构建的若依经典管理后台风格生图工作台，与 Python 后端（FastAPI + 快手可灵图片 O3 / 302.ai API）实现前后端全链路打通。

---

## 🌟 核心特性

1. **若依经典系统布局**：
   - 经典深蓝侧边栏（`#304156`）+ 菜单高亮与折叠动效
   - 顶部导航栏（折叠控制、面包屑、API 在线状态指示灯、管理员头像）
2. **多模态生图支持**：
   - **纯文生图**：输入画面提示词一键生成
   - **参考图生图（图生图）**：支持上传 1-10 张本地参考图片，后端自动转换为 302.ai 云图床 URL 传入模型
3. **丰富参数自由调控**：
   - **画面比例**：1:1、16:9、9:16、4:3、3:4、3:2、2:3、auto
   - **画质分辨率**：1K 标准、2K 高清、4K 超清
   - **生成张数**：1 - 4 张
   - **组图连贯模式**：story_mode
4. **实时渲染交互**：
   - 异步轮询任务状态（`submitted` -> `processing` -> `succeed` / `failed`）
   - 呼吸光晕加载动画与耗时/进度分段提示
5. **画廊与资产沉淀**：
   - 历史任务本地持久化存储（`data/tasks.json`）
   - 一键下载、复制图片链接、设为参考图继续创作、参数一键回填复用

---

## 🚀 启动与使用方式

### 方式一：一键前后端一体化启动（推荐）

直接在根目录下运行 Python 启动脚本，FastAPI 会自动托管构建完成的 Vue 3 工作台前端并自动打开浏览器：

```bash
# 在项目根目录执行
python start_ai_workbench.py
```
- 访问地址：`http://127.0.0.1:8000`

---

### 方式二：Vite 前端独立热更新开发模式

如果需要修改 Vue 组件源码并享受秒级热重载：

1. **启动后端 API 服务**：
   ```bash
   uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **启动 Vue 3 开发服务器**：
   ```bash
   cd ruoyi-ai-workbench
   npm run dev
   ```
   - 前端开发地址：`http://localhost:3000`（内部已配置将 `/api` 请求反向代理至 `http://127.0.0.1:8000`）

3. **打包生产静态资源**：
   ```bash
   cd ruoyi-ai-workbench
   npm run build
   ```
   打包产物将自动输出至 `dist/` 目录，供后端一体化服务加载。

---

## 📁 目录结构

```
ruoyi-ai-workbench/
├── dist/                      # Vite 生产打包产物 (供后端一体化挂载)
├── src/
│   ├── api/
│   │   └── image.js           # RESTful 接口封装 (生图、轮询、历史、上传)
│   ├── views/
│   │   └── image/
│   │       └── index.vue      # 生图工作台主视图 (参数面板 + 实时展台 + 历史画廊)
│   ├── App.vue                # 若依风格总布局 (侧边栏 + Navbar + 主路由区域)
│   └── main.js                # Vue 3 入口与 Element Plus 注册
├── standalone.html            # 单文件零构建备用前端
├── index.html                 # Vite HTML 模板入口
├── vite.config.js             # Vite 代理与路径别名配置
└── package.json               # 前端依赖配置
```
