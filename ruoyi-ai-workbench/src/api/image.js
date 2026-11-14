import axios from 'axios'

const service = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 请求拦截器：自动注入 Bearer Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：全局拦截 401 未登录并触发重定向
service.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

// ================= 认证接口 =================
export function login(data) {
  return service.post('/auth/login', data)
}

export function getCurrentUser() {
  return service.get('/auth/me')
}

export function logout() {
  return service.post('/auth/logout')
}

// ================= 生图与资产业务接口 =================
// 提交生图任务
export function generateImage(data) {
  return service.post('/image/generate', data)
}

// 轮询查询任务状态
export function getTaskStatus(taskId) {
  return service.get(`/image/task/${taskId}`)
}

// 查询历史任务与资产列表
export function listTasks(params) {
  return service.get('/image/tasks', { params })
}

// 删除资产任务
export function deleteTask(taskId) {
  return service.delete(`/image/task/${taskId}`)
}

// 上传本地参考图
export function uploadReferenceImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return service.post('/image/upload-reference', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取系统健康与模型链路信息
export function getSystemInfo() {
  return service.get('/system/info')
}

// 更新系统服务与 API Key 配置
export function updateSystemConfig(data) {
  return service.post('/system/config', data)
}

// 动态拉取 302.ai 支持的所有生图模型列表
export function list302Models(refresh = false) {
  return service.get('/models', { params: { refresh } })
}

export default service
