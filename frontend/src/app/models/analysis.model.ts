/** AI-generated candidate analysis from Gemini. */
export interface Analysis {
  candidate_id: number;
  match_percentage: number;
  summary: string;
  matching_skills: string[];
  missing_skills: string[];
  strengths: string[];
  weaknesses: string[];
  years_of_experience: string;
  hiring_recommendation: string;
  suitability_score: number;
}