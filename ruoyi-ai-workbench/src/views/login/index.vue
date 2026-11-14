<template>
  <div class="login-wrapper">
    <!-- 背景光效装饰 -->
    <div class="bg-glow bg-glow-1"></div>
    <div class="bg-glow bg-glow-2"></div>

    <div class="login-container">
      <!-- 头部品牌 Logo -->
      <div class="login-header">
        <div class="brand-icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
            <path d="M5 3v4" />
            <path d="M19 17v4" />
            <path d="M3 5h4" />
            <path d="M17 19h4" />
          </svg>
        </div>
        <h1 class="brand-title">若依 AI 生图工作台</h1>
        <p class="brand-subtitle">RuoYi AI Studio · 302.ai 全模型通用多模态视觉生成系统</p>
      </div>

      <!-- 登录表单 -->
      <div class="login-card">
        <div class="card-headline">
          <span class="headline-text">账号登录</span>
          <span class="headline-badge">生产运行环境</span>
        </div>

        <el-form :model="loginForm" :rules="rules" ref="formRef" class="login-form" size="large">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <!-- 生产合规：服务协议与隐私政策授权勾选 -->
          <div class="compliance-agreement-row">
            <el-checkbox v-model="agreeTerms">
              <span class="agreement-text">
                我已阅读并同意
                <a href="javascript:void(0)" @click.stop="showTermsModal = true">《服务协议》</a>
                与
                <a href="javascript:void(0)" @click.stop="showPrivacyModal = true">《隐私政策》</a>
              </span>
            </el-checkbox>
          </div>

          <el-button
            type="primary"
            class="btn-login-submit"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '安全验证中...' : '立即登录系统' }}
          </el-button>
        </el-form>
      </div>

      <!-- 底部合规备案与版权信息 -->
      <div class="login-footer">
        <div class="compliance-meta">
          <span>算法备案编号：网信算备 110108746200234010013 号</span>
        </div>
        <div class="copyright-meta">
          <span>© 2026 若依 AI 生图工作台 · 302.ai 全模型矩阵驱动 · All Rights Reserved</span>
        </div>
      </div>
    </div>

    <!-- 《服务协议》弹窗 -->
    <el-dialog
      v-model="showTermsModal"
      title="服务协议"
      width="600px"
      append-to-body
      class="compliance-dialog"
    >
      <div class="compliance-dialog-content">
        <h4>一、总则</h4>
        <p>欢迎使用若依 AI 生图工作台。本协议是您与平台运营方之间关于使用 AI 多模态视觉生成服务所订立的协议。请您在登录和使用前仔细阅读本协议条款。</p>
        <h4>二、服务说明与使用规范</h4>
        <p>1. 本平台提供基于深度学习算法的文本生成图像、图像生成图像等 AI 创作辅助工具。</p>
        <p>2. 用户应遵守国家法律法规及《生成式人工智能服务管理暂行办法》，不得利用本服务制作、复制、发布含有违法违规、侵犯他人肖像权/名誉权/版权、色情、暴恐、虚假信息等内容。</p>
        <p>3. 平台保留对用户提交的提示词与生成图像进行算法合规性过滤和人工抽检的权利。</p>
        <h4>三、知识产权与生成物标识</h4>
        <p>平台生成的合成内容应符合国家关于人工智能生成合成内容标识的相关规定，用户在公开传播合成成果时，应以显著方式告知社会公众该内容系由人工智能合成。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="confirmTerms">我已阅读并同意</el-button>
      </template>
    </el-dialog>

    <!-- 《隐私政策》弹窗 -->
    <el-dialog
      v-model="showPrivacyModal"
      title="隐私政策"
      width="600px"
      append-to-body
      class="compliance-dialog"
    >
      <div class="compliance-dialog-content">
        <h4>一、信息收集与使用</h4>
        <p>1. 账号信息：我们将收集您的登录用户名与认证凭证，用于身份核验与资产隔离。</p>
        <p>2. 业务日志：为保证服务稳定性与内容合规追溯，系统会记录生成任务的元数据、消耗算力、请求 IP 与操作时间戳。</p>
        <h4>二、数据安全保障</h4>
        <p>我们采用业界标准的安全防护机制（包括全链路 HTTPS 加密、密码加盐 Bcrypt 哈希、严格数据库行级租户隔离）保护您的资产与数据隐私。</p>
        <h4>三、数据储存与注销</h4>
        <p>您的生成图片与历史记录将妥善保存在私有化存储节点中，您可随时通过工作台自主删除已生成的历史资产。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="confirmPrivacy">我已阅读并同意</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login } from '../../api/image.js'

const emit = defineEmits(['login-success'])

const formRef = ref(null)
const loading = ref(false)
const agreeTerms = ref(true)
const showTermsModal = ref(false)
const showPrivacyModal = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const confirmTerms = () => {
  agreeTerms.value = true
  showTermsModal.value = false
}

const confirmPrivacy = () => {
  agreeTerms.value = true
  showPrivacyModal.value = false
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    if (!agreeTerms.value) {
      ElMessage.warning('请先阅读并勾选同意《服务协议》与《隐私政策》')
      return
    }

    loading.value = true
    try {
      const res = await login({
        username: loginForm.username.trim(),
        password: loginForm.password.trim()
      })
      const data = res.data?.data || res.data
      if (data && data.token) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('userInfo', JSON.stringify(data.user || {}))
        ElMessage.success({
          message: `欢迎回来，${data.user?.nickname || data.user?.username || '管理员'}！`,
          duration: 2500
        })
        emit('login-success', data)
      } else {
        throw new Error(res.data?.msg || '未获取到有效令牌')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.response?.data?.msg || err.message || '登录失败，请检查账号密码'
      ElMessage.error(msg)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-wrapper {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0b0f19;
  background-image: 
    radial-gradient(at 0% 0%, rgba(37, 99, 235, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.15) 0px, transparent 50%);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.bg-glow {
  position: absolute;
  width: 450px;
  height: 450px;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  opacity: 0.25;
}

.bg-glow-1 {
  top: -100px;
  left: -100px;
  background: #2563eb;
}

.bg-glow-2 {
  bottom: -100px;
  right: -100px;
  background: #0284c7;
}

.login-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 440px;
  padding: 24px;
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.brand-icon-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2563eb, #0284c7);
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.35);
  margin-bottom: 16px;
}

.brand-icon-box svg {
  width: 28px;
  height: 28px;
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  color: #f8fafc;
  letter-spacing: -0.5px;
  margin: 0 0 8px 0;
}

.brand-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.login-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 32px 28px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.card-headline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.headline-text {
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.headline-badge {
  font-size: 11px;
  font-weight: 500;
  color: #10b981;
  background: rgba(16, 185, 129, 0.12);
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.login-form :deep(.el-input__wrapper) {
  background: rgba(15, 23, 42, 0.6);
  box-shadow: none !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 6px 14px;
  color: #f8fafc;
  transition: all 0.2s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(56, 189, 248, 0.4);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #38bdf8;
  box-shadow: 0 0 0 1px #38bdf8 !important;
}

.login-form :deep(.el-input__inner) {
  color: #f8fafc;
}

.compliance-agreement-row {
  margin-top: 4px;
  margin-bottom: 18px;
}

.compliance-agreement-row :deep(.el-checkbox__label) {
  font-size: 12px;
  color: #94a3b8;
}

.agreement-text a {
  color: #38bdf8;
  text-decoration: none;
}

.agreement-text a:hover {
  text-decoration: underline;
}

.btn-login-submit {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb, #0284c7);
  border: none;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
  transition: all 0.2s ease;
}

.btn-login-submit:hover {
  background: linear-gradient(135deg, #1d4ed8, #0369a1);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 12px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.compliance-meta {
  color: #475569;
  font-size: 11px;
}

.compliance-dialog-content {
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.7;
  color: #334155;
  font-size: 13px;
}

.compliance-dialog-content h4 {
  margin: 12px 0 6px 0;
  font-weight: 600;
  color: #0f172a;
}
</style>
