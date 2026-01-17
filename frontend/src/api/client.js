// frontend/src/api/client.js
import axios from 'axios';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  // CRITICAL: This allows the browser to send the HttpOnly cookie automatically
  withCredentials: true, 
});

// We no longer need setAuthHeader because the browser handles the cookie.
export const setAuthHeader = () => {}; 

// Simplified request interceptor
api.interceptors.request.use(
  (config) => {
    // Only set Content-Type if it's not FormData
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Updated Response Interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // If we get a 401, the session/cookie is invalid
      // Only redirect if we aren't already on the login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  // No register/login here if you are using the OAuth Redirect flow
  getMe: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'), // Important: call backend to clear cookie
};

// Documents endpoints
export const documentsAPI = {
  upload: (file, docType = 'resume') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);
    
    return api.post('/documents/upload', formData);
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
  list: (status = null, type = null) => {
    const params = new URLSearchParams();
    if (status) {
      params.append('status_filter', status);
    }
    if (type) {
      params.append('type_filter', type);
    }
    const queryString = params.toString();
    return api.get(`/opportunities/${queryString ? `?${queryString}` : ''}`);
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

export const grantsAPI = {
  searchGrants: (payload) => {
    // Prune empty filters and ensure pagination.sort_order exists
    const body = { ...payload };
    if (body.filters) {
      const pruned = {};
      for (const [k, v] of Object.entries(body.filters)) {
        if (v == null) continue;
        if (Object.prototype.hasOwnProperty.call(v, 'one_of')) {
          if (Array.isArray(v.one_of) && v.one_of.length > 0) pruned[k] = { one_of: v.one_of };
        } else {
          // date or range objects: keep if any non-null field exists
          const entries = Object.entries(v).filter(([_, val]) => val !== null && val !== undefined && val !== '');
          if (entries.length) pruned[k] = Object.fromEntries(entries);
        }
      }
      body.filters = Object.keys(pruned).length ? pruned : undefined;
    }

    // Ensure pagination exists and has at least one sort_order
    body.pagination = body.pagination || { page_offset: 1, page_size: 10 };
    if (!body.pagination.sort_order || body.pagination.sort_order.length === 0) {
      body.pagination.sort_order = [{ order_by: 'post_date', sort_direction: 'descending' }];
    }

    return api.post('/grants/search', body);
  },
  getGrantSuggestions: () => api.get('/grants/suggestions'),
};

export const jobsAPI = {
  searchJobs: (payload) => {
    // Keep it simple - just pass the payload as-is
    return api.post('/jobs/search', payload);
  },
  getJobSuggestions: (country = 'us', limit = 10) => {
    const params = new URLSearchParams();
    if (country) params.append('country', country);
    if (limit) params.append('limit', limit.toString());
    return api.get(`/jobs/suggestions?${params.toString()}`);
  },
};

export default api;
