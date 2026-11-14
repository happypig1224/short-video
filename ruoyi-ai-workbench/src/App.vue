<template>
  <!-- 未登录状态：全屏展示若依风格登录认证页 -->
  <LoginPage
    v-if="!isLoggedIn"
    @login-success="handleLoginSuccess"
  />

  <!-- 已登录状态：展示完整若依 AI 生图工作台系统 -->
  <div v-else :class="['studio-app-shell', `theme-${currentTheme}`]">
    <!-- 极简高质感顶部导航栏 -->
    <header class="studio-topbar">
      <!-- 左侧：品牌与模型快速切换 -->
      <div class="topbar-left">
        <div class="brand-badge">
          <div class="brand-logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3a9 9 0 0 0 0 18v-9z" />
            </svg>
          </div>
          <span class="brand-name">Kling Studio</span>
        </div>

        <div class="topbar-divider"></div>

        <!-- 当前激活模型选择按钮 -->
        <button class="topbar-model-btn" @click="openModelPicker" title="切换模型">
          <span class="model-status-dot"></span>
          <span class="model-name-text">{{ currentModel.name }}</span>
          <el-icon class="model-chevron"><ArrowDown /></el-icon>
        </button>
      </div>

      <!-- 中间：视图切换 (创作 / 画廊) -->
      <div class="topbar-center">
        <div class="view-segmented-tabs">
          <button
            :class="['segmented-tab', { active: activeView === 'studio' }]"
            @click="activeView = 'studio'"
          >
            <el-icon :size="13"><Monitor /></el-icon>
            <span>创作</span>
          </button>
          <button
            :class="['segmented-tab', { active: activeView === 'gallery' }]"
            @click="activeView = 'gallery'"
          >
            <el-icon :size="13"><Collection /></el-icon>
            <span>画廊</span>
          </button>
        </div>
      </div>

      <!-- 右侧：算力账户、用户信息、主题切换与退出登录 -->
      <div class="topbar-right">
        <!-- 算力额度徽标 -->
        <div class="credits-badge" title="当前可用生图算力点数">
          <span class="credits-bolt">⚡</span>
          <span class="credits-label">算力</span>
          <span class="credits-val">{{ currentUser.credits !== undefined ? currentUser.credits : 9999 }}</span>
        </div>

        <!-- 用户身份标识 -->
        <div class="user-chip">
          <el-avatar :size="24" :src="currentUser.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" />
          <span class="user-nickname">{{ currentUser.nickname || currentUser.username || '管理员' }}</span>
          <span class="user-role-tag">{{ currentUser.role === 'admin' ? '主管' : '成员' }}</span>
        </div>

        <div class="topbar-divider-mini"></div>

        <!-- 浅色/深色主题切换 -->
        <button
          class="topbar-icon-btn"
          :title="currentTheme === 'light' ? '切换深色模式' : '切换浅色模式'"
          @click="toggleTheme"
        >
          <el-icon :size="15">
            <Sunny v-if="currentTheme === 'light'" />
            <Moon v-else />
          </el-icon>
        </button>

        <!-- 接口设置抽屉 -->
        <button class="topbar-icon-btn" title="服务与接口设置" @click="settingsDrawerVisible = true">
          <el-icon :size="15"><Setting /></el-icon>
        </button>

        <!-- 退出登录按钮 -->
        <button class="topbar-icon-btn btn-logout" title="退出登录" @click="handleLogout">
          <el-icon :size="15"><SwitchButton /></el-icon>
        </button>
      </div>
    </header>

    <!-- 主工作区 -->
    <main class="studio-viewport-body">
      <ImageWorkbench
        ref="workbenchRef"
        :active-view="activeView"
        :current-model="currentModel"
        :available-models="availableModels"
        :current-theme="currentTheme"
        :current-user="currentUser"
        @switch-view="activeView = $event"
        @open-model-picker="openModelPicker"
        @model-change="handleModelSelected"
        @task-created="refreshUserProfile"
      />
    </main>

    <!-- 极简模型切换弹窗 -->
    <el-dialog
      v-model="modelPickerVisible"
      title="切换生图模型"
      width="680px"
      class="minimal-dialog"
      :show-close="true"
    >
      <div class="model-picker-modal-content">
        <!-- 搜索与刷新 -->
        <div class="model-search-filter-bar">
          <el-input
            v-model="modelSearchQuery"
            placeholder="搜索模型名称或厂商 (如: kling, flux, midjourney)..."
            prefix-icon="Search"
            size="default"
            clearable
          />
          <button
            class="btn-refresh-models"
            :disabled="refreshingModels"
            @click="refreshModelsLive"
          >
            <el-icon :class="{ 'is-spinning': refreshingModels }"><Refresh /></el-icon>
            <span>{{ refreshingModels ? '拉取中' : '刷新' }}</span>
          </button>
        </div>

        <!-- 厂商过滤 Chips -->
        <div class="vendor-filter-chips">
          <button
            :class="['vendor-chip', { active: selectedVendor === '' }]"
            @click="selectedVendor = ''"
          >
            全部 ({{ availableModels.length }})
          </button>
          <button
            v-for="v in vendorList"
            :key="v"
            :class="['vendor-chip', { active: selectedVendor === v }]"
            @click="selectedVendor = v"
          >
            {{ v }}
          </button>
        </div>

        <!-- 模型列表网格 -->
        <div class="models-card-scroll-grid" v-loading="refreshingModels">
          <div
            v-for="m in filteredModelList"
            :key="m.id"
            :class="['model-select-card', { active: currentModel.id === m.id }]"
            @click="handleModelSelected(m)"
          >
            <div class="card-header-row">
              <span class="model-vendor-badge">{{ m.vendor }}</span>
              <span v-if="currentModel.id === m.id" class="model-current-active">当前使用</span>
            </div>
            <div class="model-display-name">{{ m.name }}</div>
            <div class="model-desc-text">{{ m.description }}</div>
          </div>
          <div v-if="!refreshingModels && filteredModelList.length === 0" class="model-empty-tip">
            暂无匹配的模型数据
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 接口与服务配置抽屉 -->
    <el-drawer
      v-model="settingsDrawerVisible"
      title="系统与接口配置"
      size="380px"
      direction="rtl"
    >
      <div class="drawer-inner-body">
        <el-form label-position="top">
          <el-form-item label="当前账号">
            <el-input :model-value="`${currentUser.nickname || '管理员'} (${currentUser.username || 'admin'})`" disabled />
          </el-form-item>

          <el-form-item label="当前模型">
            <el-input :model-value="`${currentModel.name}`" disabled />
          </el-form-item>

          <el-form-item label="服务节点 (Base URL)">
            <el-select v-model="configForm.baseUrl" style="width: 100%;">
              <el-option label="https://api.302.ai (默认主节点)" value="https://api.302.ai" />
              <el-option label="https://api.302ai.com (备用加速节点)" value="https://api.302ai.com" />
            </el-select>
          </el-form-item>

          <el-form-item label="302.ai API Key">
            <el-input
              v-model="configForm.apiKey"
              type="password"
              show-password
              :placeholder="systemInfo.api_key_masked ? `已配置 (${systemInfo.api_key_masked})` : 'sk-...'"
            />
            <div class="form-tip">留空则继续使用当前配置。</div>
          </el-form-item>

          <div style="display: flex; gap: 8px; margin-top: 14px;">
            <el-button type="primary" :loading="savingConfig" @click="saveConfig">保存</el-button>
            <el-button :loading="testingConnection" @click="testConnection">测试连通</el-button>
          </div>

          <el-divider />

          <div class="sys-meta-block">
            <div class="sys-row"><span>认证状态</span><code style="color:#10b981;">已登录 (JWT Bearer)</code></div>
            <div class="sys-row"><span>已载入模型</span><code>{{ availableModels.length }} 个</code></div>
            <div class="sys-row"><span>生图核心</span><code>快手可灵 O3 / 302.ai API</code></div>
            <div class="sys-row"><span>数据库存储</span><code>SQLite (workbench.db)</code></div>
            <div class="sys-row"><span>接口文档</span><a href="/docs" target="_blank">/docs</a></div>
          </div>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  Monitor,
  Collection,
  Setting,
  ArrowDown,
  Refresh,
  Search,
  Sunny,
  Moon,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import LoginPage from './views/login/index.vue'
import ImageWorkbench from './views/image/index.vue'
import {
  getCurrentUser,
  logout,
  getSystemInfo,
  updateSystemConfig,
  list302Models
} from './api/image.js'

// 用户登录鉴权状态
const token = ref(localStorage.getItem('token') || '')
const isLoggedIn = ref(!!token.value)
const currentUser = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

// 主题模式：默认浅色 light
const currentTheme = ref(localStorage.getItem('studio_theme') || 'light')

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('studio_theme', currentTheme.value)
}

const activeView = ref('studio')
const workbenchRef = ref(null)

const modelPickerVisible = ref(false)
const settingsDrawerVisible = ref(false)
const refreshingModels = ref(false)
const savingConfig = ref(false)
const testingConnection = ref(false)

const modelSearchQuery = ref('')
const selectedVendor = ref('')

const systemInfo = ref({
  model: 'klingai',
  model_name: '快手可灵图片 O3 (Kling Image O3)',
  base_url: 'https://api.302.ai',
  api_key_masked: ''
})

const configForm = reactive({
  baseUrl: 'https://api.302.ai',
  apiKey: ''
})

// 模型列表与当前选中的模型
const availableModels = ref([])
const vendorList = ref([])
const currentModel = ref({
  id: 'klingai',
  name: '快手可灵 O3 (Kling Image O3)',
  vendor: '快手可灵 (Kling AI)',
  badge: '旗舰首选',
  description: '最新 O3 神经扩散生图，支持高达 4K 画质与 10 张多图参考融合',
  is_kling: true
})

// 过滤后的模型
const filteredModelList = computed(() => {
  let list = availableModels.value
  if (selectedVendor.value) {
    list = list.filter(m => m.vendor === selectedVendor.value)
  }
  if (modelSearchQuery.value.trim()) {
    const q = modelSearchQuery.value.trim().toLowerCase()
    list = list.filter(m => m.name.toLowerCase().includes(q) || m.id.toLowerCase().includes(q) || m.vendor.toLowerCase().includes(q))
  }
  return list
})

// 登录成功回调
const handleLoginSuccess = async (data) => {
  token.value = data.token
  currentUser.value = data.user || {}
  isLoggedIn.value = true
  await initWorkbenchData()
}

// 刷新用户信息及剩余算力
const refreshUserProfile = async () => {
  try {
    const res = await getCurrentUser()
    const payload = res?.data?.data || res?.data
    if (payload) {
      currentUser.value = payload
      localStorage.setItem('userInfo', JSON.stringify(payload))
    }
  } catch (e) {
    console.warn('刷新用户信息失败', e)
  }
}

// 安全退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录系统吗？', '提示', {
    confirmButtonText: '确定退出',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await logout()
    } catch (e) {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    token.value = ''
    currentUser.value = {}
    isLoggedIn.value = false
    ElMessage.success('已安全退出')
  }).catch(() => {})
}

// 监听 401 拦截事件
const handleUnauthorized = () => {
  if (isLoggedIn.value) {
    isLoggedIn.value = false
    token.value = ''
    currentUser.value = {}
    ElMessage.warning('登录已失效，请重新登录')
  }
}

const openModelPicker = () => {
  modelPickerVisible.value = true
  if (availableModels.value.length === 0 && !refreshingModels.value) {
    refreshModelsLive()
  }
}

const handleModelSelected = (model) => {
  currentModel.value = model
  modelPickerVisible.value = false
  ElMessage.success(`已切换模型: ${model.name}`)
}

const parseModelsResponse = (res) => {
  const payload = res?.data !== undefined ? res.data : res
  let models = []
  let vendors = []
  if (Array.isArray(payload)) {
    models = payload
  } else if (payload && Array.isArray(payload.data)) {
    models = payload.data
    vendors = payload.vendors || []
  } else if (payload && Array.isArray(payload.rows)) {
    models = payload.rows
    vendors = payload.vendors || []
  }
  return { models, vendors }
}

const refreshModelsLive = async () => {
  refreshingModels.value = true
  try {
    const res = await list302Models(true)
    const { models, vendors } = parseModelsResponse(res)
    if (models.length > 0) {
      availableModels.value = models
      if (vendors.length > 0) {
        vendorList.value = vendors
      } else {
        extractVendors(models)
      }
      ElMessage.success(`已同步 ${models.length} 个最新模型`)
    } else {
      ElMessage.warning('未获取到模型列表')
    }
  } catch (e) {
    console.error('拉取模型失败', e)
  } finally {
    refreshingModels.value = false
  }
}

const extractVendors = (models) => {
  const set = new Set()
  models.forEach(m => {
    if (m.vendor) set.add(m.vendor)
  })
  vendorList.value = Array.from(set)
}

const loadSystemInfo = async () => {
  try {
    const res = await getSystemInfo()
    const payload = res?.data !== undefined ? res.data : res
    const info = payload?.data || payload
    if (info) {
      systemInfo.value = info
      configForm.baseUrl = info.base_url || 'https://api.302.ai'
    }
  } catch (e) {
    console.error('加载系统配置失败', e)
  }
}

const saveConfig = async () => {
  savingConfig.value = true
  try {
    await updateSystemConfig({
      api_key: configForm.apiKey.trim() || undefined,
      base_url: configForm.baseUrl
    })
    ElMessage.success('配置已更新')
    settingsDrawerVisible.value = false
    await loadSystemInfo()
  } catch (e) {
    ElMessage.error(`保存失败: ${e.message}`)
  } finally {
    savingConfig.value = false
  }
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    await refreshModelsLive()
    ElMessage.success('连接正常')
  } catch (e) {
    ElMessage.error('连接失败，请检查网络或配置')
  } finally {
    testingConnection.value = false
  }
}

const initWorkbenchData = async () => {
  await refreshUserProfile()
  await loadSystemInfo()
  try {
    const res = await list302Models(false)
    const { models, vendors } = parseModelsResponse(res)
    if (models.length > 0) {
      availableModels.value = models
      if (vendors.length > 0) {
        vendorList.value = vendors
      } else {
        extractVendors(models)
      }
      const defaultKling = models.find(m => m.id === 'klingai' || m.id === 'kling-v3-omni' || m.id.includes('kling'))
      if (defaultKling) {
        currentModel.value = defaultKling
      }
    }
  } catch (e) {
    console.error('初始加载模型失败', e)
  }
}

onMounted(async () => {
  window.addEventListener('auth:unauthorized', handleUnauthorized)
  if (isLoggedIn.value) {
    await initWorkbenchData()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('auth:unauthorized', handleUnauthorized)
})
</script>

<style scoped>
/* 容器架构 */
.studio-app-shell {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
  transition: background-color 0.15s ease, color 0.15s ease;
}

/* 浅色主题 Light */
.studio-app-shell.theme-light {
  background-color: #fafafa;
  color: #18181b;
  --topbar-bg: #ffffff;
  --topbar-border: #f0f0f0;
  --panel-bg: #ffffff;
  --panel-border: #f0f0f0;
  --canvas-bg: #f5f5f7;
  --text-primary: #18181b;
  --text-secondary: #71717a;
  --text-muted: #a1a1aa;
  --accent-color: #0071e3;
  --accent-hover: #0077ed;
  --accent-light: #f0f7ff;
  --control-bg: #f4f4f5;
  --control-hover: #e4e4e7;
  --control-border: #e4e4e7;
}

/* 深色主题 Dark */
.studio-app-shell.theme-dark {
  background-color: #09090b;
  color: #f4f4f5;
  --topbar-bg: #121215;
  --topbar-border: #1f1f23;
  --panel-bg: #121215;
  --panel-border: #1f1f23;
  --canvas-bg: #09090b;
  --text-primary: #f4f4f5;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;
  --accent-color: #2563eb;
  --accent-hover: #3b82f6;
  --accent-light: #172554;
  --control-bg: #1f1f23;
  --control-hover: #27272a;
  --control-border: #27272a;
}

/* 顶部导航栏 Topbar */
.studio-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
  background-color: var(--topbar-bg);
  border-bottom: 1px solid var(--topbar-border);
  z-index: 100;
  user-select: none;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  color: var(--accent-color);
}

.brand-logo-icon svg {
  width: 100%;
  height: 100%;
}

.brand-name {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--text-primary);
}

.topbar-divider {
  width: 1px;
  height: 16px;
  background-color: var(--control-border);
}

.topbar-divider-mini {
  width: 1px;
  height: 14px;
  background-color: var(--control-border);
  margin: 0 2px;
}

/* 模型选择器按钮 */
.topbar-model-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.12s ease;
}

.topbar-model-btn:hover {
  background-color: var(--control-bg);
  color: var(--text-primary);
}

.model-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #10b981;
}

.model-chevron {
  font-size: 10px;
  color: var(--text-muted);
}

/* 视图分段控制器 (中间 Tab) */
.topbar-center {
  display: flex;
  align-items: center;
}

.view-segmented-tabs {
  display: flex;
  align-items: center;
  background-color: var(--control-bg);
  padding: 2px;
  border-radius: 6px;
}

.segmented-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border: none;
  background: transparent;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.segmented-tab:hover {
  color: var(--text-primary);
}

.segmented-tab.active {
  background-color: var(--panel-bg);
  color: var(--text-primary);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

/* 右侧操作按钮 */
.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 算力额度徽标 */
.credits-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.25);
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.credits-bolt {
  font-size: 12px;
}

.credits-label {
  opacity: 0.85;
}

.credits-val {
  font-family: ui-monospace, SFMono-Regular, monospace;
}

/* 用户 Chip */
.user-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 6px 2px 2px;
  border-radius: 14px;
  background: var(--control-bg);
  font-size: 12px;
  font-weight: 500;
}

.user-nickname {
  color: var(--text-primary);
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role-tag {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  background: var(--accent-light);
  color: var(--accent-color);
  font-weight: 600;
}

.topbar-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background-color: transparent;
  border: none;
  border-radius: 5px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.topbar-icon-btn:hover {
  background-color: var(--control-bg);
  color: var(--text-primary);
}

.btn-logout:hover {
  background-color: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

/* 主工作区 Viewport Body */
.studio-viewport-body {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: var(--canvas-bg);
}

/* 极简弹窗 */
.minimal-dialog :deep(.el-dialog__header) {
  padding: 16px 20px 8px;
  border-bottom: none;
}

.minimal-dialog :deep(.el-dialog__title) {
  font-size: 15px;
  font-weight: 600;
}

.model-picker-modal-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 480px;
}

.model-search-filter-bar {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-refresh-models {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--control-border);
  background-color: var(--control-bg);
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}

.btn-refresh-models:hover:not(:disabled) {
  background-color: var(--control-hover);
}

.vendor-filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.vendor-chip {
  padding: 4px 10px;
  font-size: 11px;
  border-radius: 12px;
  border: 1px solid var(--control-border);
  background-color: var(--control-bg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.vendor-chip.active {
  background-color: var(--accent-color);
  color: #ffffff;
  border-color: var(--accent-color);
}

.models-card-scroll-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  overflow-y: auto;
  max-height: 380px;
  padding-right: 4px;
}

.model-select-card {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--control-border);
  background-color: var(--panel-bg);
  cursor: pointer;
  transition: all 0.15s ease;
}

.model-select-card:hover {
  border-color: var(--accent-color);
  transform: translateY(-1px);
}

.model-select-card.active {
  border-color: var(--accent-color);
  background-color: var(--accent-light);
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.model-vendor-badge {
  font-size: 10px;
  color: var(--text-muted);
}

.model-current-active {
  font-size: 10px;
  color: var(--accent-color);
  font-weight: 600;
}

.model-display-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.model-desc-text {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.model-empty-tip {
  grid-column: span 2;
  text-align: center;
  padding: 40px 0;
  color: var(--text-muted);
  font-size: 13px;
}

.drawer-inner-body {
  padding: 0 4px;
}

.form-tip {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.sys-meta-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
}

.sys-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-secondary);
}

.sys-row code {
  color: var(--text-primary);
  background-color: var(--control-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

.sys-row a {
  color: var(--accent-color);
  text-decoration: none;
}
</style>
