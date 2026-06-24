import { Component, Input } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { ToastService } from '../../services/toast.service';
import { MatchResult } from '../../models/match-result.model';
import { Analysis } from '../../models/analysis.model';
import { Questions } from '../../models/questions.model';
import { LoadingSpinnerComponent } from '../loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [LoadingSpinnerComponent],
  templateUrl: './results.component.html',
})
export class ResultsComponent {
  @Input() matchResults: MatchResult[] = [];
  @Input() jobDescription = '';

  // Analysis and questions state, keyed by candidate ID
  analyses: Map<number, Analysis> = new Map();
  questions: Map<number, Questions> = new Map();
  loadingAnalysis: number | null = null;
  loadingQuestions: number | null = null;
  expandedCandidate: number | null = null;

  constructor(
    private apiService: ApiService,
    private toastService: ToastService,
  ) {}

  /** Toggle the expanded view for a candidate's analysis. */
  toggleCandidate(candidateId: number): void {
    if (this.expandedCandidate === candidateId) {
      this.expandedCandidate = null;
    } else {
      this.expandedCandidate = candidateId;
    }
  }

  /** Request AI analysis for a specific candidate. */
  loadAnalysis(candidateId: number): void {
    if (this.analyses.has(candidateId)) {
      this.toggleCandidate(candidateId);
      return;
    }

    this.loadingAnalysis = candidateId;
    this.apiService.generateAnalysis(candidateId, this.jobDescription).subscribe({
      next: (analysis) => {
        this.analyses.set(candidateId, analysis);
        this.loadingAnalysis = null;
        this.expandedCandidate = candidateId;
        this.toastService.success('Analysis generated');
      },
      error: (err) => {
        this.loadingAnalysis = null;
        this.toastService.error(err.error?.detail || 'Analysis failed');
      },
    });
  }

  /** Request interview questions for a specific candidate. */
  loadQuestions(candidateId: number): void {
    if (this.questions.has(candidateId)) {
      this.expandedCandidate = candidateId;
      return;
    }

    this.loadingQuestions = candidateId;
    this.apiService.generateQuestions(candidateId, this.jobDescription).subscribe({
      next: (questions) => {
        this.questions.set(candidateId, questions);
        this.loadingQuestions = null;
        this.expandedCandidate = candidateId;
        this.toastService.success('Questions generated');
      },
      error: (err) => {
        this.loadingQuestions = null;
        this.toastService.error(err.error?.detail || 'Question generation failed');
      },
    });
  }

  /** Get the color class for a match percentage. */
  getMatchColor(percentage: number): string {
    if (percentage >= 75) return 'bg-emerald-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  }

  /** Get the badge color for a hiring recommendation. */
  getRecommendationClass(rec: string): string {
    switch (rec) {
      case 'Strong Hire': return 'bg-emerald-100 text-emerald-800';
      case 'Hire':        return 'bg-green-100 text-green-800';
      case 'Maybe':       return 'bg-yellow-100 text-yellow-800';
      case 'Not Recommended': return 'bg-red-100 text-red-800';
      default:            return 'bg-slate-100 text-slate-800';
    }
  }

  /** Get rank display. */
  getRankBadge(rank: number): string {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  }
}