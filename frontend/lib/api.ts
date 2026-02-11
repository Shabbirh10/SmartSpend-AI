import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
});

export const uploadStatement = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getTransactions = async () => {
  const response = await api.get('/transactions');
  return response.data;
};

export const getTrends = async () => {
  const response = await api.get('/analytics/trends');
  return response.data;
};

export const getSubscriptions = async () => {
  const response = await api.get('/analytics/subscriptions');
  return response.data;
};

export const downloadDemoStatement = () => {
  // Direct link trigger
  window.open(`${API_URL}/demo/download`, '_blank');
};

export const chatWithAI = async (query: string) => {
  const response = await api.post('/chat', { query });
  return response.data;
};
