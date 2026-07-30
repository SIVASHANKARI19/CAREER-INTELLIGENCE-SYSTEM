import axios from 'axios';
import {
  User, StudentProfile, ResumeAnalysis, GithubAnalysis, LinkedinAnalysis,
  FusionResult, PlacementPrediction, ReadinessScore, SkillGapResult,
  LearningRoadmap, ShapExplanation, SimulatorSession, CompanyRequirement,
  ModelRegistry, AdminAnalytics
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 4.1 Auth APIs
export const authApi = {
  register: (data: { email: string; password: string; full_name?: string; role?: 'student' | 'admin' }) =>
    apiClient.post<User>('/auth/register', data).then(r => r.data),
  login: (data: { email: string; password: string }) =>
    apiClient.post<{ access_token: string; refresh_token: string }>('/auth/login', data).then(r => r.data),
  refresh: (refresh_token: string) =>
    apiClient.post<{ access_token: string; refresh_token: string }>('/auth/refresh', { refresh_token }).then(r => r.data),
  forgotPassword: (email: string) =>
    apiClient.post<{ message: string; reset_token_mock?: string }>('/auth/forgot-password', { email }).then(r => r.data),
  resetPassword: (token: string, new_password: string) =>
    apiClient.post<{ message: string }>('/auth/reset-password', { token, new_password }).then(r => r.data),
  getMe: () =>
    apiClient.get<User>('/auth/me').then(r => r.data),
};

// 4.2 Profile APIs
export const profileApi = {
  getProfile: () =>
    apiClient.get<StudentProfile>('/profile').then(r => r.data),
  updateProfile: (data: Partial<StudentProfile>) =>
    apiClient.put<StudentProfile>('/profile', data).then(r => r.data),
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<{ message: string; resume_file_path: string }>('/profile/resume-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data);
  },
  uploadLinkedin: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<{ message: string; linkedin_pdf_path: string }>('/profile/linkedin-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data);
  },
  getCompletion: () =>
    apiClient.get<{ student_id: number; completion_percentage: number; missing_fields: string[] }>('/profile/completion').then(r => r.data),
};

// 4.3 Dashboard API
export const dashboardApi = {
  getSummary: () =>
    apiClient.get<any>('/dashboard/summary').then(r => r.data),
};

// 4.4 Resume Analyzer API
export const resumeApi = {
  analyze: (student_id?: number) =>
    apiClient.post<ResumeAnalysis>('/resume/analyze', { student_id }).then(r => r.data),
  getAnalysis: (student_id: number) =>
    apiClient.get<ResumeAnalysis>(`/resume/${student_id}`).then(r => r.data),
};

// 4.5 GitHub Analyzer API
export const githubApi = {
  analyze: (github_url: string) =>
    apiClient.post<GithubAnalysis>('/github/analyze', { github_url }).then(r => r.data),
  getAnalysis: (student_id: number) =>
    apiClient.get<GithubAnalysis>(`/github/${student_id}`).then(r => r.data),
};

// 4.6 LinkedIn Analyzer API
export const linkedinApi = {
  analyze: (student_id?: number) =>
    apiClient.post<LinkedinAnalysis>('/linkedin/analyze', { student_id }).then(r => r.data),
  getAnalysis: (student_id: number) =>
    apiClient.get<LinkedinAnalysis>(`/linkedin/${student_id}`).then(r => r.data),
};

// 4.7 Fusion Engine API
export const fusionApi = {
  runFusion: (student_id?: number) =>
    apiClient.post<FusionResult>('/profile/fusion', { student_id }).then(r => r.data),
  getFusion: (student_id: number) =>
    apiClient.get<FusionResult>(`/profile/fusion/${student_id}`).then(r => r.data),
};

// 4.8 Placement Prediction API
export const predictionApi = {
  predict: (student_id?: number) =>
    apiClient.post<PlacementPrediction>('/predict-placement', { student_id }).then(r => r.data),
  getPrediction: (student_id: number) =>
    apiClient.get<PlacementPrediction>(`/predict-placement/${student_id}`).then(r => r.data),
};

// 4.9 Readiness API
export const readinessApi = {
  getReadiness: (student_id: number) =>
    apiClient.get<ReadinessScore>(`/readiness/${student_id}`).then(r => r.data),
};

// 4.10 Skill Gap API
export const skillGapApi = {
  analyze: (target_role: string, student_id?: number) =>
    apiClient.post<SkillGapResult>('/skill-gap', { target_role, student_id }).then(r => r.data),
  getSkillGap: (student_id: number, target_role?: string) =>
    apiClient.get<SkillGapResult>(`/skill-gap/${student_id}`, { params: { target_role } }).then(r => r.data),
};

// 4.11 Learning Roadmap API
export const roadmapApi = {
  generate: (student_id?: number) =>
    apiClient.post<LearningRoadmap>('/roadmap', { student_id }).then(r => r.data),
  getRoadmap: (student_id: number) =>
    apiClient.get<LearningRoadmap>(`/roadmap/${student_id}`).then(r => r.data),
};

// 4.12 Explainable AI (SHAP) API
export const shapApi = {
  generate: (prediction_id: number) =>
    apiClient.post<ShapExplanation>('/shap', { prediction_id }).then(r => r.data),
  getShap: (prediction_id: number) =>
    apiClient.get<ShapExplanation>(`/shap/${prediction_id}`).then(r => r.data),
};

// 4.13 Career Simulator API
export const simulatorApi = {
  simulate: (applied_changes: { action: string; category?: string }[], student_id?: number) =>
    apiClient.post<SimulatorSession>('/career-simulator', { applied_changes, student_id }).then(r => r.data),
};

// 4.14 Admin APIs
export const adminApi = {
  getStudents: (params?: { skip?: number; limit?: number; department?: string; career_goal?: string }) =>
    apiClient.get<StudentProfile[]>('/admin/students', { params }).then(r => r.data),
  getStudentDetail: (id: number) =>
    apiClient.get<StudentProfile>(`/admin/students/${id}`).then(r => r.data),
  createCompanyRequirement: (data: Partial<CompanyRequirement>) =>
    apiClient.post<CompanyRequirement>('/admin/company-requirements', data).then(r => r.data),
  getCompanyRequirements: () =>
    apiClient.get<CompanyRequirement[]>('/admin/company-requirements').then(r => r.data),
  updateCompanyRequirement: (id: number, data: Partial<CompanyRequirement>) =>
    apiClient.put<CompanyRequirement>(`/admin/company-requirements/${id}`, data).then(r => r.data),
  retrainModel: () =>
    apiClient.post<any>('/admin/model/retrain').then(r => r.data),
  getModelRegistry: () =>
    apiClient.get<ModelRegistry[]>('/admin/model/registry').then(r => r.data),
  getAnalytics: () =>
    apiClient.get<AdminAnalytics>('/admin/analytics').then(r => r.data),
};
