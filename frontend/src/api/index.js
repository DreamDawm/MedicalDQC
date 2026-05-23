import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const datasourceApi = {
  list: () => api.get('/datasources'),
  get: (id) => api.get(`/datasources/${id}`),
  create: (data) => api.post('/datasources', data),
  update: (id, data) => api.put(`/datasources/${id}`, data),
  delete: (id) => api.delete(`/datasources/${id}`),
  test: (id) => api.post(`/datasources/${id}/test`),
  getTables: (id) => api.get(`/datasources/${id}/tables`),
  getColumns: (id, table) => api.get(`/datasources/${id}/tables/${table}/columns`),
}

export const builtinRuleApi = {
  list: () => api.get('/builtin-rules'),
  get: (id) => api.get(`/builtin-rules/${id}`),
}

export const validationRuleApi = {
  list: (params) => api.get('/validation-rules', { params }),
  create: (data) => api.post('/validation-rules', data),
  update: (id, data) => api.put(`/validation-rules/${id}`, data),
  delete: (id) => api.delete(`/validation-rules/${id}`),
}

export const taskApi = {
  list: () => api.get('/tasks'),
  create: (data) => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  run: (id) => api.post(`/tasks/${id}/run`),
  getProgress: (id) => api.get(`/tasks/${id}/current`),
}

export const resultApi = {
  list: (params) => api.get('/results', { params }),
  get: (id) => api.get(`/results/${id}`),
  trend: (params) => api.get('/results/trend', { params }),
  reportUrl: (id) => `/api/results/${id}/report`,
  reportViewUrl: (id) => `/api/results/${id}/report/view`,
  delete: (id) => api.delete(`/results/${id}`),
}
