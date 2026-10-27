import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const DEFAULT_API_KEY = 'ai-wf-key-default-admin-2026';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-KEY': DEFAULT_API_KEY,
  },
  timeout: 45000,
});

// Dashboard stats
export const fetchDashboardStats = async () => {
  const response = await apiClient.get('/stats');
  return response.data;
};

// Workflows API
export const fetchWorkflows = async (params = {}) => {
  const response = await apiClient.get('/workflows', { params });
  return response.data;
};

export const fetchWorkflowById = async (id) => {
  const response = await apiClient.get(`/workflows/${id}`);
  return response.data;
};

export const createWorkflow = async (workflowData) => {
  const response = await apiClient.post('/workflows', workflowData);
  return response.data;
};

export const updateWorkflow = async (id, workflowData) => {
  const response = await apiClient.put(`/workflows/${id}`, workflowData);
  return response.data;
};

export const deleteWorkflow = async (id) => {
  const response = await apiClient.delete(`/workflows/${id}`);
  return response.data;
};

export const executeWorkflow = async (id, triggerPayload = {}, runAsync = false) => {
  const response = await apiClient.post(`/workflows/${id}/execute`, {
    trigger_payload: triggerPayload,
    run_async: runAsync,
  });
  return response.data;
};

export const importWorkflowTemplate = async (templateData) => {
  const response = await apiClient.post('/workflows/import', templateData);
  return response.data;
};

export const exportWorkflowById = async (id) => {
  const response = await apiClient.get(`/workflows/${id}/export`);
  return response.data;
};

// Executions API
export const fetchExecutions = async (params = {}) => {
  const response = await apiClient.get('/executions', { params });
  return response.data;
};

export const fetchExecutionById = async (id) => {
  const response = await apiClient.get(`/executions/${id}`);
  return response.data;
};

export const fetchExecutionLogs = async (id) => {
  const response = await apiClient.get(`/executions/${id}/logs`);
  return response.data;
};

export const cancelExecution = async (id) => {
  const response = await apiClient.post(`/executions/${id}/cancel`);
  return response.data;
};

export const retryExecution = async (id) => {
  const response = await apiClient.post(`/executions/${id}/retry`);
  return response.data;
};

// Integrations API
export const testEmailDispatch = async (payload) => {
  const response = await apiClient.post('/integrations/test-email', payload);
  return response.data;
};

export const fetchEmailOutbox = async (limit = 50) => {
  const response = await apiClient.get('/integrations/email-outbox', { params: { limit } });
  return response.data;
};

export const testWebhookDispatch = async (payload) => {
  const response = await apiClient.post('/integrations/test-webhook', payload);
  return response.data;
};

export const testLLMCompletion = async (payload) => {
  const response = await apiClient.post('/integrations/test-llm', payload);
  return response.data;
};

export default apiClient;
