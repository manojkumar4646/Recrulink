/** A single candidate match result returned by the backend. */
export interface MatchResult {
  candidate_id: number;
  name: string;
  email: string | null;
  phone: string | null;
  file_name: string;
  similarity_score: number;
  match_percentage: number;
  rank: number;
}

/** Full match response containing all results. */
export interface MatchResponse {
  matches: MatchResult[];
  total_candidates: number;
}

/** Request body for matching candidates against a job description. */
export interface MatchRequest {
  job_description: string;
  top_k: number;
}