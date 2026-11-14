<template>
  <div class="enterprise-workbench-root">
    <!-- 视图 1: 创作控制台 (Studio) -->
    <div v-show="activeView === 'studio'" class="studio-two-pane-layout">
      <!-- 左侧：参数控制面板 (Control Dock) -->
      <aside class="studio-control-dock">
        <div class="control-scroll-body">
          <!-- 1. 生图提示词 -->
          <div class="form-section">
            <div class="section-header">
              <span class="section-title">提示词</span>
              <div class="section-meta">
                <button v-if="form.prompt" class="btn-text-action" @click="form.prompt = ''">清空</button>
                <span class="counter-label">{{ form.prompt.length }}/1000</span>
              </div>
            </div>

            <div class="prompt-input-wrapper">
              <textarea
                v-model="form.prompt"
                rows="4"
                class="minimal-textarea"
                placeholder="描述画面主体、构图视角、光照环境与质感细节... (Ctrl + Enter 快速生成)"
                maxlength="1000"
                @keydown.ctrl.enter="handleCtrlEnter"
              ></textarea>
            </div>
          </div>

          <!-- 2. 参考图 (图生图) -->
          <div class="form-section">
            <div class="section-header">
              <span class="section-title">参考图</span>
              <span v-if="form.referenceImages.length > 0" class="counter-label">{{ form.referenceImages.length }}/10</span>
            </div>

            <div class="ref-thumbnails-track">
              <div
                v-for="(img, idx) in form.referenceImages"
                :key="idx"
                class="ref-thumb-item"
              >
                <img :src="img" class="ref-thumb-img" />
                <button class="ref-remove-icon" title="移除" @click="removeRefImage(idx)">×</button>
              </div>

              <!-- 上传按钮 -->
              <div
                v-if="form.referenceImages.length < 10"
                class="ref-upload-tile"
                :class="{ uploading }"
                title="上传参考图 (支持拖拽/点击)"
                @click="triggerFileInput"
              >
                <el-icon v-if="!uploading" :size="14"><Plus /></el-icon>
                <el-icon v-else :size="14" class="is-loading"><Loading /></el-icon>
                <span class="upload-caption">{{ uploading ? '上传中' : '添加' }}</span>
              </div>
            </div>
            <input ref="fileInput" type="file" style="display: none;" accept="image/*" @change="onFileSelected" />
          </div>

          <!-- 3. 画面比例 -->
          <div class="form-section">
            <div class="section-header">
              <span class="section-title">画面比例</span>
              <span class="active-pill-val">{{ form.aspectRatio }}</span>
            </div>

            <div class="ratio-matrix-row">
              <button
                v-for="r in aspectRatios"
                :key="r.value"
                type="button"
                :class="['ratio-pill-btn', { active: form.aspectRatio === r.value }]"
                @click="form.aspectRatio = r.value"
              >
                <span class="ratio-preview-box">
                  <span class="ratio-box-shape" :style="r.boxStyle"></span>
                </span>
                <span class="ratio-val-text">{{ r.label }}</span>
              </button>
            </div>
          </div>

          <!-- 4. 输出规格 (画质) -->
          <div class="form-section">
            <div class="section-header">
              <span class="section-title">画质分辨率</span>
            </div>
            <div class="segmented-pill-bar">
              <button
                v-for="res in [
                  { label: '1K 标准', val: '1k' },
                  { label: '2K 超清', val: '2k' },
                  { label: '4K 影视', val: '4k' }
                ]"
                :key="res.val"
                type="button"
                :class="['seg-pill-btn', { active: form.imgResolution === res.val }]"
                @click="form.imgResolution = res.val"
              >
                {{ res.label }}
              </button>
            </div>
          </div>

          <!-- 5. 生成数量 -->
          <div class="form-section">
            <div class="section-header">
              <span class="section-title">生成数量</span>
            </div>
            <div class="segmented-pill-bar">
              <button
                v-for="cnt in [1, 2, 4]"
                :key="cnt"
                type="button"
                :class="['seg-pill-btn', { active: form.imageCount === cnt }]"
                @click="form.imageCount = cnt"
              >
                {{ cnt }} 张
              </button>
            </div>
          </div>

          <!-- 6. 连贯组图开关 -->
          <div class="form-section toggle-section">
            <div class="toggle-text-block">
              <div class="toggle-title">连贯模式</div>
              <div class="toggle-desc">保持角色形象与风格连贯一致</div>
            </div>
            <el-switch v-model="form.storyMode" />
          </div>
        </div>

        <!-- 底部主提交操作栏 -->
        <div class="control-footer-action">
          <button
            type="button"
            class="btn-generate-main"
            :disabled="generating"
            @click="startGenerate"
          >
            <el-icon v-if="generating" class="is-loading"><Loading /></el-icon>
            <el-icon v-else :size="15"><Picture /></el-icon>
            <span>{{ generating ? `可灵 O3 渲染中 (${formattedTimer})...` : '生成图片' }}</span>
            <kbd v-if="!generating" class="shortcut-badge">Ctrl ↵</kbd>
          </button>
        </div>
      </aside>

      <!-- 右侧：作品展示舞台 (Stage Viewport) -->
      <section class="studio-stage-viewport">
        <!-- 舞台展示区 (纯净实色，无任何噪点杂质) -->
        <div class="stage-canvas-area">
          <!-- 1. 正在渲染中状态 -->
          <div v-if="generating" class="stage-generating-state">
            <div class="generating-card">
              <div class="generating-spinner">
                <el-icon :size="28" class="is-loading"><Loading /></el-icon>
              </div>
              <div class="generating-title">快手可灵 O3 正在渲染中</div>
              <div class="generating-timer">已耗时: {{ formattedTimer }} (通常约需 20~40 秒)</div>
              <div class="generating-prompt-snip">“{{ form.prompt }}”</div>
            </div>
          </div>

          <!-- 2. 展示当前成果图像 (大图呈现 + 极简浮动工具条) -->
          <div v-else-if="currentResult && currentResult.result_images && currentResult.result_images.length > 0" class="stage-artwork-presentation">
            <!-- 顶部浮动工具条 -->
            <div class="artwork-top-actions">
              <div class="artwork-meta-pill">
                <span class="meta-item bold">{{ currentResult.model_name || currentModel.name }}</span>
                <span class="meta-dot">·</span>
                <span class="meta-item">{{ currentResult.aspect_ratio || '1:1' }}</span>
                <span class="meta-dot">·</span>
                <span class="meta-item">{{ (currentResult.img_resolution || '2k').toUpperCase() }}</span>
                <span v-if="currentResult.cost_time" class="meta-dot">·</span>
                <span v-if="currentResult.cost_time" class="meta-item timer">{{ (currentResult.cost_time / 1000).toFixed(1) }}s</span>
              </div>

              <div class="artwork-tool-btns">
                <button class="tool-btn" title="全屏查看原图" @click="previewFullImage(activeDisplayImage)">
                  <el-icon><ZoomIn /></el-icon>
                  <span>查看原图</span>
                </button>
                <button class="tool-btn" title="下载高清图" @click="downloadUrl(activeDisplayImage, 0)">
                  <el-icon><Download /></el-icon>
                  <span>下载</span>
                </button>
                <button class="tool-btn" title="复制图片链接" @click="copyText(activeDisplayImage)">
                  <el-icon><Link /></el-icon>
                  <span>复制链接</span>
                </button>
                <button class="tool-btn highlight" title="将此图的提示词与参数回填到左侧" @click="reuseTask(currentResult)">
                  <el-icon><Refresh /></el-icon>
                  <span>复用参数</span>
                </button>
              </div>
            </div>

            <!-- 主图画框 -->
            <div class="artwork-frame">
              <img
                :src="activeDisplayImage"
                class="artwork-img"
                title="点击全屏查看原图"
                @click="previewFullImage(activeDisplayImage)"
              />
            </div>

            <!-- 多张生成时的缩略图条 (生成 2P/4P 时展示) -->
            <div v-if="currentResult.result_images.length > 1" class="artwork-multi-tabs">
              <div
                v-for="(imgUrl, idx) in currentResult.result_images"
                :key="idx"
                :class="['multi-tab-item', { active: activeDisplayImage === imgUrl }]"
                @click="activeDisplayImage = imgUrl"
              >
                <img :src="imgUrl" />
                <span class="tab-index-badge">#{{ idx + 1 }}</span>
              </div>
            </div>

            <!-- 底部提示词条 -->
            <div class="artwork-prompt-line">
              <span class="prompt-text-content" :title="currentResult.prompt">{{ currentResult.prompt }}</span>
              <button class="btn-copy-link" @click="copyText(currentResult.prompt)">
                <el-icon><DocumentCopy /></el-icon>
                <span>复制提示词</span>
              </button>
            </div>
          </div>

          <!-- 3. 无任务时的极简迎宾态 -->
          <div v-else class="stage-empty-view">
            <div class="empty-content-box">
              <div class="empty-mark-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </div>
              <div class="empty-headline">开始创作</div>
              <div class="empty-subheadline">在左侧设置提示词与画面比例，点击「生成图片」开启渲染</div>

              <div class="inspiration-row">
                <button
                  v-for="(item, idx) in inspirationPrompts"
                  :key="idx"
                  class="inspiration-btn"
                  @click="applyInspiration(item)"
                >
                  {{ item.title }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部：近期成果流 (Recent Rail) -->
        <div class="stage-bottom-rail">
          <div class="rail-header-line">
            <span class="rail-heading">近期成果</span>
            <button class="rail-all-link" @click="emitSwitchView('gallery')">
              <span>查看全部画廊</span>
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>

          <div class="rail-track">
            <div
              v-for="item in recentCreations"
              :key="item.task_id"
              :class="['rail-card-thumb', { active: currentResult && currentResult.task_id === item.task_id }]"
              :title="item.prompt"
              @click="loadResultToStage(item)"
            >
              <img
                v-if="item.result_images && item.result_images.length > 0"
                :src="item.result_images[0]"
                class="thumb-img"
              />
              <div v-else class="thumb-empty">
                {{ item.task_status === 'failed' ? '失败' : '处理中' }}
              </div>
              <span class="thumb-ratio-tag">{{ item.aspect_ratio || '1:1' }}</span>
            </div>
            <div v-if="recentCreations.length === 0" class="rail-empty-tip">暂无历史作品</div>
          </div>
        </div>
      </section>
    </div>

    <!-- 视图 2: 资产画廊 (Gallery) -->
    <div v-show="activeView === 'gallery'" class="gallery-full-layout">
      <!-- 顶部控制条 -->
      <div class="gallery-toolbar-top">
        <div class="gallery-filters">
          <el-input
            v-model="searchPrompt"
            placeholder="搜索提示词关键词..."
            prefix-icon="Search"
            size="default"
            clearable
            style="width: 260px;"
            @change="loadHistory"
          />
          <div class="ratio-chips-group">
            <button
              :class="['ratio-chip-btn', { active: currentFilterRatio === '' }]"
              @click="setFilterRatio('')"
            >
              全部画幅
            </button>
            <button
              v-for="r in ['1:1', '16:9', '9:16', '4:3', '3:4', '3:2', '2:3']"
              :key="r"
              :class="['ratio-chip-btn', { active: currentFilterRatio === r }]"
              @click="setFilterRatio(r)"
            >
              {{ r }}
            </button>
          </div>
        </div>

        <div class="gallery-actions-right">
          <span class="gallery-count-text">共 {{ filteredHistoryList.length }} 件资产</span>
          <el-button size="default" :icon="Refresh" @click="loadHistory">刷新</el-button>
          <el-button type="primary" size="default" @click="emitSwitchView('studio')">返回工作台</el-button>
        </div>
      </div>

      <!-- 画廊瀑布流展示区 -->
      <div class="gallery-wall-scroll">
        <div v-if="filteredHistoryList.length > 0" class="gallery-grid-wall">
          <div
            v-for="item in filteredHistoryList"
            :key="item.task_id"
            class="gallery-tile-card"
          >
            <div class="tile-image-box">
              <img
                v-if="item.result_images && item.result_images.length > 0"
                :src="item.result_images[0]"
                class="tile-img"
                loading="lazy"
                @click="previewFullImage(item.result_images[0])"
              />
              <div v-else class="tile-placeholder">
                {{ item.task_status === 'failed' ? '渲染异常' : '处理中' }}
              </div>
              <div class="tile-tag-badges">
                <span class="tile-badge-ratio">{{ item.aspect_ratio }}</span>
                <span class="tile-badge-res">{{ item.img_resolution }}</span>
              </div>
            </div>

            <div class="tile-body-info">
              <div class="tile-prompt-snip" :title="item.prompt">{{ item.prompt }}</div>
              <div class="tile-meta-footer">
                <span class="tile-time-text">{{ item.create_time ? item.create_time.slice(5, 16) : '' }}</span>
                <div class="tile-btns">
                  <button class="tile-btn-action" @click="reuseTask(item)">复用</button>
                  <button
                    v-if="item.result_images && item.result_images.length > 0"
                    class="tile-btn-action"
                    @click="downloadUrl(item.result_images[0], 0)"
                  >
                    下载
                  </button>
                  <button class="tile-btn-action danger" @click="deleteHistoryTask(item.task_id)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="gallery-empty-state">
          <el-icon :size="40" color="#a1a1aa"><FolderOpened /></el-icon>
          <div class="empty-main">暂无生成资产</div>
          <div class="empty-sub">在工作台生成的所有画作均会在此自动归档保存</div>
        </div>
      </div>
    </div>

    <!-- 全屏灯箱图片查看器 -->
    <el-image-viewer
      v-if="fullPreviewVisible"
      :url-list="[previewUrl]"
      @close="fullPreviewVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  Picture,
  ArrowRight,
  Plus,
  Loading,
  Refresh,
  DocumentCopy,
  Download,
  Link,
  ZoomIn,
  FolderOpened
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  generateImage,
  getTaskStatus,
  listTasks,
  deleteTask,
  uploadReferenceImage
} from '../../api/image.js'

const props = defineProps({
  activeView: {
    type: String,
    default: 'studio'
  },
  currentModel: {
    type: Object,
    default: () => ({
      id: 'klingai',
      name: '快手可灵 O3 (Kling Image O3)',
      vendor: '快手可灵 (Kling AI)'
    })
  },
  availableModels: {
    type: Array,
    default: () => []
  },
  currentTheme: {
    type: String,
    default: 'light'
  },
  currentUser: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['switch-view', 'open-model-picker', 'model-change', 'task-created'])

const emitSwitchView = (v) => emit('switch-view', v)

// 核心参数表单
const form = reactive({
  prompt: '',
  referenceImages: [],
  aspectRatio: '1:1',
  imgResolution: '2k',
  imageCount: 1,
  storyMode: false
})

// 灵感示例词
const inspirationPrompts = [
  {
    title: '3D 黏土卡通',
    prompt: 'chibi avatar, cute 3D cartoon anthropomorphic pig, chubby face, friendly happy smile, wearing red bib overalls, smooth stylized clay texture, Pixar and Pop Mart style, studio soft lighting, close-up portrait, clean background, 8k, Octane render'
  },
  {
    title: '雨夜赛博写实',
    prompt: '电影级写实摄影，未来赛博朋克雨夜街道，霓虹灯光倒影在湿润的沥青路面，雨丝细节，哈苏中画幅长焦镜头，冷暖对比色调，8k超高清'
  },
  {
    title: '意境水墨山水',
    prompt: '传统中国写意水墨山水画，云雾缭绕中的古风水榭楼阁，孤舟蓑笠翁，水晕墨章，浓淡相宜，极简留白美学，宣纸微质感'
  }
]

const applyInspiration = (item) => {
  form.prompt = item.prompt
  ElMessage.success(`已填入: ${item.title}`)
}

// 比例数据及紧凑图标
const aspectRatios = [
  { label: '1:1', value: '1:1', boxStyle: { width: '10px', height: '10px' } },
  { label: '16:9', value: '16:9', boxStyle: { width: '13px', height: '7px' } },
  { label: '9:16', value: '9:16', boxStyle: { width: '7px', height: '13px' } },
  { label: '4:3', value: '4:3', boxStyle: { width: '12px', height: '9px' } },
  { label: '3:4', value: '3:4', boxStyle: { width: '9px', height: '12px' } },
  { label: '3:2', value: '3:2', boxStyle: { width: '12px', height: '8px' } },
  { label: '2:3', value: '2:3', boxStyle: { width: '8px', height: '12px' } }
]

// 运行与轮询状态
const generating = ref(false)
const uploading = ref(false)
const currentTaskId = ref('')
const elapsedSeconds = ref(0)
const currentResult = ref(null)
const activeDisplayImage = ref('')
let timer = null
let pollTimer = null

// 历史画廊
const historyList = ref([])
const searchPrompt = ref('')
const currentFilterRatio = ref('')
const fileInput = ref(null)

// 全屏预览
const fullPreviewVisible = ref(false)
const previewUrl = ref('')

const formattedTimer = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`
})

// 近期成果（取历史前 12 条）
const recentCreations = computed(() => {
  return historyList.value.slice(0, 12)
})

const filteredHistoryList = computed(() => {
  let list = historyList.value
  if (currentFilterRatio.value) {
    list = list.filter(item => item.aspect_ratio === currentFilterRatio.value)
  }
  return list
})

const setFilterRatio = (r) => {
  currentFilterRatio.value = r
}

const handleCtrlEnter = () => {
  if (!generating.value) {
    startGenerate()
  }
}

// 载入结果到主舞台
const loadResultToStage = (item) => {
  currentResult.value = item
  currentTaskId.value = item.task_id || ''
  if (item.result_images && item.result_images.length > 0) {
    activeDisplayImage.value = item.result_images[0]
  }
}

// 复用历史任务参数
const reuseTask = (item) => {
  form.prompt = item.prompt || ''
  form.aspectRatio = item.aspect_ratio || '1:1'
  form.imgResolution = item.img_resolution || '2k'
  form.imageCount = item.image_count || 1
  if (item.reference_images && item.reference_images.length > 0) {
    form.referenceImages = [...item.reference_images]
  }
  emitSwitchView('studio')
  ElMessage.success('已回填参数至工作台')
}

// 复制文本
const copyText = (text) => {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.info('复制失败，请手动选中复制')
  })
}

// 下载原图
const downloadUrl = (url, idx = 0) => {
  if (!url) return
  const a = document.createElement('a')
  a.href = url
  const prefix = (props.currentModel?.id || 'ai_image').replace(/[^a-zA-Z0-9_-]/g, '_')
  a.download = `${prefix}_${Date.now()}_${idx + 1}.png`
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// 全屏大图预览
const previewFullImage = (url) => {
  if (!url) return
  previewUrl.value = url
  fullPreviewVisible.value = true
}

// 参考图上传处理
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const onFileSelected = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('参考图大小不能超过 10MB')
    return
  }

  uploading.value = true
  try {
    const res = await uploadReferenceImage(file)
    if (res.data && res.data.file_url) {
      form.referenceImages.push(res.data.file_url)
      ElMessage.success('参考图上传成功')
    }
  } catch (err) {
    ElMessage.error(`上传失败: ${err.message}`)
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const removeRefImage = (index) => {
  form.referenceImages.splice(index, 1)
}

// 启动生图
const startGenerate = async () => {
  if (!form.prompt.trim()) {
    ElMessage.warning('请先输入生图提示词')
    return
  }

  generating.value = true
  elapsedSeconds.value = 0

  clearInterval(timer)
  timer = setInterval(() => {
    elapsedSeconds.value++
  }, 1000)

  try {
    const res = await generateImage({
      prompt: form.prompt.trim(),
      reference_images: form.referenceImages,
      aspect_ratio: form.aspectRatio,
      img_resolution: form.imgResolution,
      image_count: form.imageCount,
      story_mode: form.storyMode,
      model_id: props.currentModel.id
    })

    const payload = res.data?.data || res.data
    if (payload && payload.task_id) {
      currentTaskId.value = payload.task_id
      emit('task-created')
      startPolling(payload.task_id)
    } else {
      throw new Error('未返回任务 ID')
    }
  } catch (e) {
    generating.value = false
    clearInterval(timer)
    ElMessage.error(`提交失败: ${e.message}`)
  }
}

// 轮询任务状态
const startPolling = (taskId) => {
  clearInterval(pollTimer)

  pollTimer = setInterval(async () => {
    try {
      const res = await getTaskStatus(taskId)
      const data = res.data
      if (!data) return

      if (data.task_status === 'succeed') {
        clearInterval(pollTimer)
        clearInterval(timer)
        generating.value = false
        currentResult.value = data
        if (data.result_images && data.result_images.length > 0) {
          activeDisplayImage.value = data.result_images[0]
        }
        ElMessage.success('渲染完成')
        await loadHistory()
      } else if (data.task_status === 'failed') {
        clearInterval(pollTimer)
        clearInterval(timer)
        generating.value = false
        ElMessage.error(`生图失败: ${data.status_msg || '模型生成异常'}`)
      }
    } catch (e) {
      console.warn('轮询中...', e)
    }
  }, 3000)
}

// 加载历史任务
const loadHistory = async () => {
  try {
    const res = await listTasks({
      prompt: searchPrompt.value.trim(),
      pageSize: 40
    })
    if (res.data) {
      const payload = res.data
      const items = Array.isArray(payload) ? payload : (payload.rows || payload.data || [])
      historyList.value = items
    }
  } catch (e) {
    console.error('加载历史记录失败', e)
  }
}

const deleteHistoryTask = async (taskId) => {
  try {
    await deleteTask(taskId)
    ElMessage.success('已删除')
    await loadHistory()
    if (currentResult.value && currentResult.value.task_id === taskId) {
      currentResult.value = historyList.value.find(h => h.result_images && h.result_images.length > 0) || null
      if (currentResult.value && currentResult.value.result_images) {
        activeDisplayImage.value = currentResult.value.result_images[0]
      }
    }
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  await loadHistory()
  if (historyList.value && historyList.value.length > 0) {
    const successItem = historyList.value.find(h => h.result_images && h.result_images.length > 0)
    if (successItem) {
      loadResultToStage(successItem)
    }
  }
})

onBeforeUnmount(() => {
  clearInterval(timer)
  clearInterval(pollTimer)
})
</script>

<style scoped>
.enterprise-workbench-root {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

/* 左右分栏 */
.studio-two-pane-layout {
  display: flex;
  width: 100%;
  height: 100%;
}

/* 左侧控制面板 (310px 紧凑干练) */
.studio-control-dock {
  width: 310px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--panel-bg);
  border-right: 1px solid var(--panel-border);
  height: 100%;
  overflow: hidden;
}

.control-scroll-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 表单组通用 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.section-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-text-action {
  background: transparent;
  border: none;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
}

.btn-text-action:hover {
  color: var(--text-primary);
}

.counter-label {
  font-size: 11px;
  color: var(--text-muted);
}

.active-pill-val {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
  background-color: var(--control-bg);
  padding: 1px 6px;
  border-radius: 4px;
}

/* 提示词输入 */
.prompt-input-wrapper {
  width: 100%;
}

.minimal-textarea {
  width: 100%;
  padding: 9px 11px;
  font-size: 12.5px;
  line-height: 1.5;
  color: var(--text-primary);
  background-color: var(--control-bg);
  border: 1px solid transparent;
  border-radius: 6px;
  resize: vertical;
  min-height: 84px;
  box-sizing: border-box;
  font-family: inherit;
  outline: none;
  transition: all 0.12s ease;
}

.minimal-textarea:focus {
  background-color: var(--panel-bg);
  border-color: var(--control-border);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

/* 参考图区域 */
.ref-thumbnails-track {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ref-thumb-item {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 5px;
  overflow: hidden;
  border: 1px solid var(--control-border);
}

.ref-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ref-remove-icon {
  position: absolute;
  top: 1px;
  right: 1px;
  width: 14px;
  height: 14px;
  background-color: rgba(0, 0, 0, 0.65);
  color: #fff;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  cursor: pointer;
}

.ref-remove-icon:hover {
  background-color: #ef4444;
}

.ref-upload-tile {
  width: 44px;
  height: 44px;
  border: 1px dashed var(--control-border);
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  color: var(--text-muted);
  background-color: var(--control-bg);
  transition: all 0.12s ease;
}

.ref-upload-tile:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

.upload-caption {
  font-size: 9px;
  transform: scale(0.85);
}

/* 比例分段矩阵 */
.ratio-matrix-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 5px;
}

.ratio-pill-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 6px 4px;
  background-color: var(--control-bg);
  border: 1px solid transparent;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.12s ease;
}

.ratio-pill-btn:hover {
  background-color: var(--control-hover);
}

.ratio-pill-btn.active {
  background-color: var(--text-primary);
  color: var(--topbar-bg);
}

.ratio-preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
}

.ratio-box-shape {
  border: 1.2px solid var(--text-secondary);
  border-radius: 1px;
  transition: border-color 0.12s ease;
}

.ratio-pill-btn.active .ratio-box-shape {
  border-color: var(--topbar-bg);
}

.ratio-val-text {
  font-size: 11px;
  font-weight: 500;
  color: inherit;
}

/* 分段条 (画质 / 张数) */
.segmented-pill-bar {
  display: flex;
  background-color: var(--control-bg);
  padding: 2px;
  border-radius: 6px;
}

.seg-pill-btn {
  flex: 1;
  padding: 5px 0;
  border: none;
  background: transparent;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  text-align: center;
  transition: all 0.12s ease;
}

.seg-pill-btn:hover {
  color: var(--text-primary);
}

.seg-pill-btn.active {
  background-color: var(--panel-bg);
  color: var(--text-primary);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

/* 连贯模式 Switch */
.toggle-section {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
}

.toggle-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.toggle-desc {
  font-size: 10.5px;
  color: var(--text-muted);
}

/* 底部操作条 */
.control-footer-action {
  padding: 10px 14px;
  border-top: 1px solid var(--panel-border);
  background-color: var(--panel-bg);
}

.btn-generate-main {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 8px 0;
  background-color: var(--text-primary);
  color: var(--topbar-bg);
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.12s ease;
}

.btn-generate-main:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-generate-main:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.shortcut-badge {
  font-family: inherit;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.15);
  color: inherit;
}

/* 右侧舞台 Viewport */
.studio-stage-viewport {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: var(--canvas-bg);
}

/* 舞台核心区域 (纯净实色，无打扰) */
.stage-canvas-area {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  overflow: hidden;
}

/* 1. 渲染中加载卡片 */
.stage-generating-state {
  display: flex;
  align-items: center;
  justify-content: center;
}

.generating-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 32px;
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  max-width: 440px;
  text-align: center;
}

.generating-spinner {
  color: var(--text-primary);
  margin-bottom: 12px;
}

.generating-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.generating-timer {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.generating-prompt-snip {
  font-size: 11.5px;
  color: var(--text-muted);
  line-height: 1.45;
  background-color: var(--control-bg);
  padding: 8px 12px;
  border-radius: 6px;
  max-height: 70px;
  overflow-y: auto;
}

/* 2. 成果呈现视图 */
.stage-artwork-presentation {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
  gap: 8px;
}

.artwork-top-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2px;
  flex-shrink: 0;
}

.artwork-meta-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-secondary);
}

.artwork-meta-pill .bold {
  font-weight: 600;
  color: var(--text-primary);
}

.artwork-meta-pill .timer {
  color: #10b981;
  font-weight: 500;
}

.meta-dot {
  color: var(--text-muted);
}

.artwork-tool-btns {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-secondary);
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.12s ease;
}

.tool-btn:hover {
  color: var(--text-primary);
  background-color: var(--control-bg);
}

.tool-btn.highlight {
  color: var(--text-primary);
  border-color: var(--control-border);
  font-weight: 600;
}

/* 主图画框 */
.artwork-frame {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-height: 0;
}

.artwork-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  cursor: zoom-in;
  transition: transform 0.12s ease;
}

.artwork-img:hover {
  transform: scale(1.004);
}

/* 多张生成选项卡 */
.artwork-multi-tabs {
  display: flex;
  justify-content: center;
  gap: 6px;
  flex-shrink: 0;
}

.multi-tab-item {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 5px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
}

.multi-tab-item.active {
  border-color: var(--text-primary);
}

.multi-tab-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tab-index-badge {
  position: absolute;
  bottom: 1px;
  right: 1px;
  font-size: 8px;
  background: rgba(0, 0, 0, 0.65);
  color: #fff;
  padding: 1px 3px;
  border-radius: 2px;
}

/* 底部提示词条 */
.artwork-prompt-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 7px 12px;
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 6px;
  flex-shrink: 0;
}

.prompt-text-content {
  font-size: 11.5px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-copy-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  font-size: 11px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}

.btn-copy-link:hover {
  text-decoration: underline;
}

/* 3. 初始空状态 */
.stage-empty-view {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-content-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 420px;
  text-align: center;
}

.empty-mark-icon {
  width: 40px;
  height: 40px;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.empty-mark-icon svg {
  width: 100%;
  height: 100%;
}

.empty-headline {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.empty-subheadline {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.inspiration-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
}

.inspiration-btn {
  padding: 4px 10px;
  font-size: 11px;
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.inspiration-btn:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

/* 底部近期成果条 (Recent Rail) */
.stage-bottom-rail {
  height: 74px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--panel-bg);
  border-top: 1px solid var(--panel-border);
  padding: 6px 16px;
  gap: 4px;
}

.rail-header-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rail-heading {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
}

.rail-all-link {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  background: transparent;
  border: none;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
}

.rail-all-link:hover {
  color: var(--text-primary);
}

.rail-track {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.rail-card-thumb {
  position: relative;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--panel-border);
  cursor: pointer;
  transition: all 0.12s ease;
}

.rail-card-thumb:hover {
  border-color: var(--control-border);
}

.rail-card-thumb.active {
  border-color: var(--text-primary);
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: var(--text-muted);
  background-color: var(--control-bg);
}

.thumb-ratio-tag {
  position: absolute;
  bottom: 1px;
  right: 1px;
  font-size: 8px;
  font-weight: 500;
  background-color: rgba(0, 0, 0, 0.65);
  color: #ffffff;
  padding: 0 2px;
  border-radius: 2px;
  transform: scale(0.8);
  transform-origin: bottom right;
}

.rail-empty-tip {
  font-size: 11px;
  color: var(--text-muted);
  padding: 4px 0;
}

/* 视图 2: 资产画廊 */
.gallery-full-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: var(--canvas-bg);
}

.gallery-toolbar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: var(--panel-bg);
  border-bottom: 1px solid var(--panel-border);
  flex-shrink: 0;
}

.gallery-filters {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ratio-chips-group {
  display: flex;
  align-items: center;
  gap: 5px;
}

.ratio-chip-btn {
  padding: 3px 8px;
  font-size: 11px;
  background-color: var(--control-bg);
  border: 1px solid transparent;
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.ratio-chip-btn:hover {
  color: var(--text-primary);
}

.ratio-chip-btn.active {
  background-color: var(--text-primary);
  color: var(--topbar-bg);
  font-weight: 500;
}

.gallery-actions-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gallery-count-text {
  font-size: 11px;
  color: var(--text-muted);
}

.gallery-wall-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 18px 20px;
}

.gallery-grid-wall {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
}

.gallery-tile-card {
  display: flex;
  flex-direction: column;
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 6px;
  overflow: hidden;
  transition: all 0.12s ease;
}

.gallery-tile-card:hover {
  border-color: var(--control-border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.tile-image-box {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background-color: var(--control-bg);
  overflow: hidden;
}

.tile-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: zoom-in;
}

.tile-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--text-muted);
}

.tile-tag-badges {
  position: absolute;
  top: 6px;
  left: 6px;
  display: flex;
  gap: 3px;
}

.tile-badge-ratio,
.tile-badge-res {
  font-size: 9px;
  font-weight: 500;
  padding: 1px 4px;
  background-color: rgba(0, 0, 0, 0.65);
  color: #fff;
  border-radius: 2px;
}

.tile-body-info {
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tile-prompt-snip {
  font-size: 11.5px;
  color: var(--text-primary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 32px;
}

.tile-meta-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--panel-border);
  padding-top: 6px;
}

.tile-time-text {
  font-size: 10px;
  color: var(--text-muted);
}

.tile-btns {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tile-btn-action {
  background: transparent;
  border: 1px solid var(--panel-border);
  border-radius: 3px;
  font-size: 10px;
  color: var(--text-secondary);
  padding: 1px 5px;
  cursor: pointer;
  transition: all 0.12s ease;
}

.tile-btn-action:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

.tile-btn-action.danger:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.gallery-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 6px;
}

.empty-main {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-sub {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
