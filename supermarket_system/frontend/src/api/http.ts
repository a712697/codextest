import axios from 'axios'

export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

http.interceptors.response.use((response) => {
  const payload = response.data
  if (payload.code !== 0) {
    return Promise.reject(new Error(payload.message || '请求失败'))
  }
  return payload.data
})
