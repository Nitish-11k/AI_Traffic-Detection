import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for video processing
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export interface Violation {
  id: string;
  type: string;
  timestamp: string;
  confidence: number;
  location: { x: number; y: number };
  vehicle_id: string;
  frame_number: number;
  details?: any;
}

export interface ViolationStats {
  total_violations: number;
  by_type: {
    red_light: number;
    wrong_side: number;
    no_helmet: number;
  };
  recent_violations: number;
  violation_rate: number;
}

export interface UploadResponse {
  status: string;
  filename: string;
  violations: Violation[];
  total_violations: number;
}

export const apiService = {
  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Upload and process video
  async uploadVideo(file: FormData): Promise<UploadResponse> {
    const response = await api.post('/upload-video', file, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all violations
  async getViolations(): Promise<{ violations: Violation[]; statistics: ViolationStats }> {
    const response = await api.get('/violations');
    return response.data;
  },

  // Get specific violation
  async getViolation(violationId: string): Promise<Violation> {
    const response = await api.get(`/violations/${violationId}`);
    return response.data;
  },

  // Get violation statistics
  async getViolationStats(): Promise<ViolationStats> {
    const response = await api.get('/violations');
    return response.data.statistics;
  },
};

export default api;

