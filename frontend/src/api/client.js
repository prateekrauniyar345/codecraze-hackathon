import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Documents endpoints
export const documentsAPI = {
  upload: (file, docType = 'resume') => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/documents/upload?doc_type=${docType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/documents/'),
  get: (id) => api.get(`/documents/${id}`),
  getText: (id) => api.get(`/documents/${id}/text`),
  delete: (id) => api.delete(`/documents/${id}`),
};

// Profiles endpoints
export const profilesAPI = {
  create: (data) => api.post('/profiles/', data),
  createFromDocument: (documentId) => api.post(`/profiles/from-document/${documentId}`),
  list: () => api.get('/profiles/'),
  getLatest: () => api.get('/profiles/latest'),
  get: (id) => api.get(`/profiles/${id}`),
  update: (id, data) => api.patch(`/profiles/${id}`, data),
  delete: (id) => api.delete(`/profiles/${id}`),
};

// Opportunities endpoints
export const opportunitiesAPI = {
  create: (data) => api.post('/opportunities/', data),
  analyze: (data) => api.post('/opportunities/analyze', data),
  analyzeExisting: (id, profileId = null) => {
    const params = profileId ? `?profile_id=${profileId}` : '';
    return api.post(`/opportunities/${id}/analyze${params}`);
  },
  list: (status = null) => {
    const params = status ? `?status_filter=${status}` : '';
    return api.get(`/opportunities/${params}`);
  },
  get: (id) => api.get(`/opportunities/${id}`),
  update: (id, data) => api.patch(`/opportunities/${id}`, data),
  delete: (id) => api.delete(`/opportunities/${id}`),
};

// Materials endpoints
export const materialsAPI = {
  generate: (data) => api.post('/materials/generate', data),
  getForOpportunity: (opportunityId) => api.get(`/materials/opportunity/${opportunityId}`),
  get: (id) => api.get(`/materials/${id}`),
  delete: (id) => api.delete(`/materials/${id}`),
};

export default api;
