import http from './http'

export const testApi = () => {
  return http.get('/getFuncList')
}

export const startDev = () => {
  return http.get('/start')
}
export const downTemplate = () => {
  return http.downGet('/download_dev_profile')
}

export const addDev = (data) => {
  return http.post('/add_device', data)
}

export const getDevDetail = (hostname) => {
  return http.get(`/update_que?hostname=${hostname}`)
}

export const editDevDetail = (data) => {
  return http.post('/update_dev', data)
}

export const getDevList = (skip, limit) => {
  return http.get(`/get_dev?skip=${skip}&limit=${limit}`)
}
export const getDevHost = (hostname) => {
  return http.get(`/que_host?hostname=${hostname}`)
}

export const getDevListTotal = () => {
  return http.get('/get_count')
}

export const delDevice = (id) => {
  return http.get(`/del?id_name=${id}`)
}

export const getBackupConfig = () => {
  return http.get('/backup_config')
}

