/** A single interview question with its strategic rationale. */
export interface InterviewQuestion {
  question: string;
  rationale: string;
}

/** AI-generated interview questions from Gemini. */
export interface Questions {
  candidate_id: number;
  technical_questions: InterviewQuestion[];
  project_questions: InterviewQuestion[];
  behavioral_questions: InterviewQuestion[];
}