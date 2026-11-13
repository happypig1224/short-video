<template>
  <div :class="['studio-app-shell', `theme-${currentTheme}`]">
    <!-- 极简高质感顶部导航栏 (Apple Native / Linear Style) -->
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

      <!-- 右侧：主题模式切换与接口配置 -->
      <div class="topbar-right">
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
        @switch-view="activeView = $event"
        @open-model-picker="openModelPicker"
        @model-change="handleModelSelected"
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
            <div class="sys-row"><span>已载入模型</span><code>{{ availableModels.length }} 个</code></div>
            <div class="sys-row"><span>生图核心</span><code>快手可灵 O3 / 302.ai API</code></div>
            <div class="sys-row"><span>接口文档</span><a href="/docs" target="_blank">/docs</a></div>
          </div>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Monitor,
  Collection,
  Setting,
  ArrowDown,
  Refresh,
  Search,
  Sunny,
  Moon
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ImageWorkbench from './views/image/index.vue'
import { getSystemInfo, updateSystemConfig, list302Models } from './api/image.js'

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
    ElMessage.warning('拉取模型失败，使用本地预设')
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

onMounted(async () => {
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

/* 浅色主题 Light (Apple / Linear Neutral) */
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

/* 深色主题 Dark (Apple / Linear Dark Neutral) */
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

/* 顶部导航栏 (46px macOS 级别紧凑高度) */
.studio-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 46px;
  padding: 0 16px;
  background-color: var(--topbar-bg);
  border-bottom: 1px solid var(--topbar-border);
  flex-shrink: 0;
  z-index: 50;
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
  user-select: none;
}

.brand-logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 5px;
  background-color: var(--text-primary);
  color: var(--topbar-bg);
}

.brand-logo-icon svg {
  width: 14px;
  height: 14px;
}

.brand-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.topbar-divider {
  width: 1px;
  height: 14px;
  background-color: var(--topbar-border);
}

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
  gap: 6px;
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

.minimal-dialog :deep(.el-dialog__body) {
  padding: 8px 20px 20px;
}

.model-search-filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.btn-refresh-models {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0 10px;
  background: transparent;
  border: 1px solid var(--control-border);
  border-radius: 5px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
}

.btn-refresh-models:hover {
  color: var(--text-primary);
  border-color: var(--text-primary);
}

.vendor-filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 12px;
}

.vendor-chip {
  padding: 3px 9px;
  background-color: var(--control-bg);
  border: none;
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.vendor-chip:hover {
  color: var(--text-primary);
}

.vendor-chip.active {
  background-color: var(--text-primary);
  color: var(--topbar-bg);
  font-weight: 500;
}

.models-card-scroll-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 2px;
}

.model-empty-tip {
  grid-column: 1 / -1;
  text-align: center;
  padding: 36px 0;
  font-size: 13px;
  color: var(--text-muted);
}

.model-select-card {
  padding: 10px 12px;
  background-color: var(--control-bg);
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.12s ease;
}

.model-select-card:hover {
  background-color: var(--panel-bg);
  border-color: var(--control-border);
}

.model-select-card.active {
  background-color: var(--panel-bg);
  border-color: var(--text-primary);
}

.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.model-vendor-badge {
  font-size: 11px;
  color: var(--text-muted);
}

.model-current-active {
  font-size: 10px;
  font-weight: 600;
  color: #10b981;
}

.model-display-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.model-desc-text {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.35;
}

/* 抽屉元信息 */
.sys-meta-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.sys-row {
  display: flex;
  justify-content: space-between;
}

.sys-row code {
  font-family: monospace;
  background-color: var(--control-bg);
  padding: 2px 6px;
  border-radius: 4px;
}

.form-tip {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}
</style>
