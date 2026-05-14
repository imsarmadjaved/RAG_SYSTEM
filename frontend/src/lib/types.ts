export interface User {
  id: string;
  email: string;
  full_name: string;
  user_type: "candidate" | "recruiter";
  company?: string;
  is_active: boolean;
  created_at: string;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  current_stage: string;
  message: string;
  error?: string;
}

export interface ChatResponse {
  answer: string;
  confidence_score: number;
  confidence_level: string;
  sources: { chunk_id: string; chunk_text: string; chunk_type: string; relevance_score: number }[];
  session_id: string;
}

export interface CandidateResult {
  email: string;
  match_score: number;
  skills_matched: string[];
  skills_missing: string[];
  experience_years: number;
  education: string;
  summary: string;
}

export interface SearchResponse {
  results: CandidateResult[];
  total_results: number;
  query_analysis: Record<string, any>;
}
