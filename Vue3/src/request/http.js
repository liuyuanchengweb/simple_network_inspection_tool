import Axios from 'axios'
import { ElMessage } from 'element-plus'

const axios = Axios.create({
  timeout: 10 * 6 * 1000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  baseURL: process.env.NODE_ENV === 'development' ? '/api' : '/API',
})

axios.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  (response) => {
    if (response.headers['content-disposition']) {
      return Promise.resolve(response)
    }
    return Promise.resolve(response.data)
  },
  (error) => {
    switch (error.response.status) {
      case 302:
        ElMessage.error('对象已移动')
        break
      case 400:
        ElMessage.error('错误的请求')
        break
      case 401:
        ElMessage.error('访问被拒绝')
        break
      case 403:
        ElMessage.error('权限过期，请重新登录！')
        break
      case 404:
        ElMessage.error('未找到')
        break
      case 500:
        ElMessage.error('服务器错误')
        break
      case 502:
        ElMessage.error('Web 服务器用作网关或代理服务器时收到了无效响应')
        break
      case 503:
        ElMessage.error('服务不可用')
        break
      case 504:
        ElMessage.error('网关超时')
        break
    }
    return Promise.reject(error)
  }
)

export default {
  post(url, data, headers) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'POST',
        url,
        data: data,
        headers: headers ? headers : {},
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  delete(url, data, headers) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'DELETE',
        url,
        data: data,
        headers: headers ? headers : {},
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  put(url, data, headers) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'PUT',
        url,
        data: data,
        headers: headers ? headers : {},
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  patch(url, data, headers) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'PATCH',
        url,
        data: data,
        headers: headers ? headers : {},
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  get(url, params) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'GET',
        url,
        params: params,
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  down(url, data, headers) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'POST',
        url,
        data: data,
        headers: headers ? headers : {},
        responseType: 'blob',
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
  downGet(url, data, headers) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'GET',
        url,
        data: data,
        headers: headers ? headers : {},
        responseType: 'blob',
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  upload(url, data, headers, onUploadProgress) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'POST',
        url,
        data: data,
        headers: headers ? headers : {},
        onUploadProgress: onUploadProgress,
      })
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
}
