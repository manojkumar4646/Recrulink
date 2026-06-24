import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  UploadResponse,
  Candidate,
} from '../models/candidate.model';
import {
  MatchResponse,
  MatchRequest,
} from '../models/match-result.model';
import { Analysis } from '../models/analysis.model';
import { Questions } from '../models/questions.model';

/**
 * API service for communicating with the RecruLink FastAPI backend.
 * All HTTP calls to the backend go through this service.
 */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /** Upload one or more resume files (PDF/DOCX). */
  uploadResumes(files: File[]): Observable<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    return this.http.post<UploadResponse>(`${this.baseUrl}/upload-resumes`, formData);
  }

  /** Match candidates against a job description. */
  matchCandidates(request: MatchRequest): Observable<MatchResponse> {
    return this.http.post<MatchResponse>(`${this.baseUrl}/match-candidates`, request);
  }

  /** Get details for a specific candidate. */
  getCandidate(id: number): Observable<Candidate> {
    return this.http.get<Candidate>(`${this.baseUrl}/candidate/${id}`);
  }

  /** Generate AI analysis for a candidate against a job description. */
  generateAnalysis(candidateId: number, jobDescription: string): Observable<Analysis> {
    return this.http.post<Analysis>(`${this.baseUrl}/generate-analysis`, {
      candidate_id: candidateId,
      job_description: jobDescription,
    });
  }

  /** Generate interview questions for a candidate. */
  generateQuestions(candidateId: number, jobDescription: string): Observable<Questions> {
    return this.http.post<Questions>(`${this.baseUrl}/generate-questions`, {
      candidate_id: candidateId,
      job_description: jobDescription,
    });
  }

  /** List all uploaded candidates. */
  listCandidates(): Observable<Candidate[]> {
    return this.http.get<Candidate[]>(`${this.baseUrl}/candidates`);
  }

  /** Clear all data (candidates, chunks, FAISS index). */
  clearAll(): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/clear`);
  }

  /** Health check. */
  healthCheck(): Observable<{ status: string; faiss_vectors: number }> {
    return this.http.get<{ status: string; faiss_vectors: number }>(`${this.baseUrl}/health`);
  }
}