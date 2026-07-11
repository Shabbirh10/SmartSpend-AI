import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';

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

export const getTaskStatus = async (taskId: string) => {
  const response = await api.get(`/tasks/${taskId}`);
  return response.data;
};

export const getTransactions = async (page = 1, perPage = 10) => {
  const response = await api.get('/transactions', { params: { page, per_page: perPage } });
  return response.data;
};

export const getTrends = async () => {
  const response = await api.get('/analytics/trends');
  return response.data;
};

export const getSubscriptions = async (page = 1, perPage = 6) => {
  const response = await api.get('/analytics/subscriptions', { params: { page, per_page: perPage } });
  return response.data;
};

export const downloadDemoStatement = () => {
  window.open('/demo_statement.pdf', '_blank');
};

export const getPortfolio = async () => {
  const response = await api.get('/portfolio');
  return response.data;
};

export const addInvestment = async (ticker: string, shares: number, price: number) => {
  const response = await api.post('/portfolio/add', { ticker, shares, price });
  return response.data;
};

export const chatWithAI = async (query: string) => {
  const response = await api.post('/chat', { query });
  return response.data;
};

export const getTickerHistory = async (ticker: string = 'SPY') => {
  const response = await api.get('/portfolio/history', { params: { ticker } });
  return response.data;
};

export const getIndianFinancialNews = async () => {
  const response = await api.get('/news');
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/analytics/categories');
  return response.data;
};
