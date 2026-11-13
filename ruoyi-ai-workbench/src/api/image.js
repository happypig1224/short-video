import axios from 'axios'

const service = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 提交生图任务
export function generateImage(data) {
  return service.post('/image/generate', data)
}

// 轮询查询任务状态
export function getTaskStatus(taskId) {
  return service.get(`/image/task/${taskId}`)
}

// 查询历史任务列表
export function listTasks(params) {
  return service.get('/image/tasks', { params })
}

// 删除任务
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


