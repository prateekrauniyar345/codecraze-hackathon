import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  // Don't set default Content-Type - let axios handle it automatically
  // JSON requests will get application/json, FormData will get multipart/form-data
});



export const setAuthHeader = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    console.log('Auth header set with token:', token.substring(0, 20) + '...');
  } else {
    delete api.defaults.headers.common['Authorization'];
    console.log('Auth header cleared');
  }
};

// Add request interceptor to attach token from localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log("token in client.js is : ", token);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Request interceptor: Adding token to', config.url);
    } else {
      console.log('Request interceptor: No token found for', config.url);
    }
    
    // Set Content-Type to application/json for non-FormData requests
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    // For FormData, axios will automatically set Content-Type with boundary
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('401 Unauthorized error:', error.config?.url);
      
      // Don't redirect on auth endpoints
      if (error.config?.url?.includes('/auth/login') || 
          error.config?.url?.includes('/auth/register')) {
        return Promise.reject(error);
      }
      
      console.warn('Redirecting to login due to 401 error');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setAuthHeader(null);
      
      // Use a slight delay to prevent race conditions
      setTimeout(() => {
        window.location.href = '/login';
      }, 100000);
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => {
    console.log("authAPI.getMe() called. Call stack follows:");
    console.trace();
    return api.get('/auth/me');
  },
};

// Documents endpoints
export const documentsAPI = {
  upload: (file, docType = 'resume') => {
    console.log('Uploading file:', file); // Log the actual file object
    console.log('File details:', {
      name: file?.name,
      size: file?.size,
      type: file?.type
    });
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Log FormData entries
    for (let pair of formData.entries()) {
      console.log('FormData entry:', pair[0], pair[1]);
    }
    
    return api.post(`/documents/upload?doc_type=${docType}`, formData);
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
