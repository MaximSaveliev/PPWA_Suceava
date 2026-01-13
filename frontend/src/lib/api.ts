import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/auth/register', { email, username, password });
    return response.data;
  },
};

export const userApi = {
  getMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
  updateMe: async (data: any) => {
    const response = await api.put('/users/me', data);
    return response.data;
  },
  update: async (userId: number, data: any) => {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  },
  getAll: async () => {
    const response = await api.get('/users/');
    return response.data;
  },
  delete: async (userId: number) => {
    await api.delete(`/users/${userId}`);
  },
};

export const subscriptionApi = {
  getPlans: async () => {
    const response = await api.get('/subscriptions/plans');
    return response.data;
  },
  getMy: async () => {
    const response = await api.get('/subscriptions/my-subscription');
    return response.data;
  },
  upgrade: async (planId: number) => {
    const response = await api.post('/subscriptions/upgrade', { plan_id: planId });
    return response.data;
  },
};

export const imageApi = {
  process: async (file: File, operation: string, params?: any) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('operation', operation);
    
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          formData.append(key, params[key].toString());
        }
      });
    }

    const response = await api.post('/images/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob',
    });
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/images/history');
    return response.data;
  },
};
