/** Candidate metadata from the database. */
export interface Candidate {
  id: number;
  name: string | null;
  email: string | null;
  phone: string | null;
  file_name: string;
  uploaded_at: string;
}

/** Upload response from the backend. */
export interface UploadResponse {
  message: string;
  filenames: string[];
  candidate_ids: number[];
}