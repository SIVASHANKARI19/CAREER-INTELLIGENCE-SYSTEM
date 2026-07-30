export type UserRole = 'student' | 'admin';

export interface User {
  id: number;
  email: string;
  role: UserRole;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  full_name?: string;
  phone?: string;
  department?: string;
  cgpa?: number;
  year_of_study?: number;
  career_goal?: string;
  programming_languages: string[];
  projects: Record<string, any>[];
  certifications: Record<string, any>[];
  internships: Record<string, any>[];
  achievements: string[];
  github_url?: string;
  resume_file_path?: string;
  linkedin_pdf_path?: string;
  profile_completion_pct: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeAnalysis {
  id: number;
  student_id: number;
  raw_text?: string;
  extracted_skills: string[];
  extracted_projects: Record<string, any>[];
  extracted_certifications: Record<string, any>[];
  extracted_experience: Record<string, any>[];
  extracted_education: Record<string, any>[];
  ats_score: number;
  suggestions: string[];
  analyzed_at: string;
}

export interface GithubAnalysis {
  id: number;
  student_id: number;
  repositories: Record<string, any>[];
  languages_summary: Record<string, any>;
  total_commits: number;
  github_score: number;
  project_quality_score: number;
  skill_confidence: Record<string, number>;
  analyzed_at: string;
}

export interface LinkedinAnalysis {
  id: number;
  student_id: number;
  headline?: string;
  summary?: string;
  extracted_skills: string[];
  extracted_experience: Record<string, any>[];
  extracted_education: Record<string, any>[];
  extracted_certificates: Record<string, any>[];
  analyzed_at: string;
}

export interface FusionResult {
  id: number;
  student_id: number;
  verified_skills: string[];
  hidden_skills: string[];
  unsupported_claims: string[];
  resume_credibility_score: number;
  suggestions: string[];
  generated_at: string;
}

export interface PlacementPrediction {
  id: number;
  student_id: number;
  placement_probability: number;
  expected_salary_range: string;
  confidence: number;
  readiness_level: 'beginner' | 'intermediate' | 'industry_ready';
  model_version: string;
  feature_snapshot: Record<string, any>;
  predicted_at: string;
}

export interface ReadinessScore {
  id: number;
  student_id: number;
  technical_readiness: number;
  communication_readiness: number;
  resume_readiness: number;
  project_readiness: number;
  github_readiness: number;
  interview_readiness: number;
  overall_readiness: number;
  computed_at: string;
}

export interface SkillGapResult {
  id: number;
  student_id: number;
  target_role: string;
  matched_skills: string[];
  missing_skills: string[];
  priority_map: Record<string, string>;
  estimated_learning_time: Record<string, string>;
  generated_at: string;
}

export interface LearningRoadmap {
  id: number;
  student_id: number;
  weekly_plan: Record<string, any>[];
  monthly_plan: Record<string, any>[];
  recommended_projects: Record<string, any>[];
  recommended_courses: Record<string, any>[];
  interview_questions: Record<string, any>[];
  resources: Record<string, any>[];
  generated_at: string;
}

export interface ShapFeatureImpact {
  feature: string;
  impact: number;
}

export interface ShapExplanation {
  id: number;
  prediction_id: number;
  positive_features: ShapFeatureImpact[];
  negative_features: ShapFeatureImpact[];
  base_value: number;
  output_value: number;
  waterfall_data: Record<string, any>[];
}

export interface SimulatorSession {
  id: number;
  student_id: number;
  baseline_probability: number;
  applied_changes: Record<string, any>[];
  simulated_probability: number;
  delta: number;
  created_at: string;
}

export interface CompanyRequirement {
  id: number;
  company_name: string;
  role: string;
  required_skills: string[];
  min_cgpa?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ModelRegistry {
  id: number;
  model_name: string;
  version: string;
  status: 'active' | 'archived' | 'training';
  trained_at: string;
  metrics: Record<string, any>;
}

export interface AdminAnalytics {
  total_students: number;
  avg_readiness_score: number;
  avg_ats_score: number;
  avg_placement_probability: number;
  industry_ready_count: number;
  top_missing_skills: { skill: string; count: number }[];
  department_stats: { department: string; students: number; avg_readiness: number }[];
}
