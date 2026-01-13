import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 统一处理响应数据
    return response.data;
  },
  (error) => {
    // 统一处理错误
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// FAQ查询相关API
export const queryApi = {
  // 自然语言查询FAQ
  queryFAQ: (question) => {
    return api.post('/query', { question });
  },
  // 反馈查询结果
  feedbackQuery: (queryId, isHelpful, rating, comment) => {
    return api.post('/query/feedback', { queryId, isHelpful, rating, comment });
  },
};

// 文档管理相关API
export const documentApi = {
  // 获取文档列表
  getDocuments: (params) => {
    return api.get('/documents', { params });
  },
  // 获取单个文档
  getDocument: (id) => {
    return api.get(`/documents/${id}`);
  },
  // 创建文档
  createDocument: (data) => {
    return api.post('/documents', data);
  },
  // 更新文档
  updateDocument: (id, data) => {
    return api.put(`/documents/${id}`, data);
  },
  // 删除文档
  deleteDocument: (id) => {
    return api.delete(`/documents/${id}`);
  },
  // 批量上传文档
  uploadDocuments: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};