import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const getSessionId = () => {
    let sid = localStorage.getItem('docchat_session_id');
    if (!sid) {
        sid = uuidv4();
        localStorage.setItem('docchat_session_id', sid);
    }
    return sid;
};

export const sessionId = getSessionId();

// ✅ Create instance WITHOUT Content-Type header
const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

// ✅ Add JSON header only for non-FormData requests
api.interceptors.request.use((config) => {
    if (!(config.data instanceof FormData)) {
        config.headers['Content-Type'] = 'application/json';
    }
    return config;
});

export const documentService = {
    upload: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', sessionId);
        
        const response = await api.post('/documents/upload', formData);
        return response.data;
    },
    list: async () => {
        const response = await api.get(`/documents/${sessionId}`);
        return response.data;
    },
    remove: async (docId) => {
        const response = await api.delete(`/documents/${docId}`);
        return response.data;
    }
};

export const chatService = {
    query: async (query, docId = null) => {
        const response = await api.post('/chat/query', {
            query,
            session_id: sessionId,
            doc_id: docId
        });
        return response.data;
    },
    getHistory: async () => {
        const response = await api.get(`/chat/${sessionId}`);
        return response.data;
    },
    clearHistory: async () => {
        const response = await api.delete(`/chat/${sessionId}`);
        return response.data;
    }
};

export default api;