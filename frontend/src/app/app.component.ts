import { Component, ViewChild } from '@angular/core';
import { ApiService } from './services/api.service';
import { ToastService } from './services/toast.service';
import { MatchResult } from './models/match-result.model';
import { ResumeUploadComponent } from './components/resume-upload/resume-upload.component';
import { JobDescriptionComponent } from './components/job-description/job-description.component';
import { ResultsComponent } from './components/results/results.component';
import { ToastComponent } from './components/toast/toast.component';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    ResumeUploadComponent,
    JobDescriptionComponent,
    ResultsComponent,
    ToastComponent,
    LoadingSpinnerComponent,
  ],
  templateUrl: './app.component.html',
})
export class AppComponent {
  matchResults: MatchResult[] = [];
  jobDescription = '';
  isMatching = false;

  // Access child components to clear their local state
  @ViewChild(ResumeUploadComponent) uploadComponent!: ResumeUploadComponent;
  @ViewChild(JobDescriptionComponent) jobComponent!: JobDescriptionComponent;

  constructor(
    private apiService: ApiService,
    private toastService: ToastService,
  ) {}

  /** Handle successful file uploads. */
  onFilesUploaded(filenames: string[]): void {
    this.toastService.info(`${filenames.length} resume(s) ready for matching`);
  }

  /** Handle job description submission: trigger candidate matching. */
  onJobSubmit(jobDescription: string): void {
    this.jobDescription = jobDescription;
    this.isMatching = true;
    this.matchResults = [];

    this.apiService.matchCandidates({
      job_description: jobDescription,
      top_k: 5,
    }).subscribe({
      next: (response) => {
        this.isMatching = false;
        this.matchResults = response.matches;
        if (response.matches.length === 0) {
          this.toastService.info('No matching candidates found');
        } else {
          this.toastService.success(`Found ${response.matches.length} matching candidate(s)`);
        }
        setTimeout(() => {
          document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
        }, 200);
      },
      error: (err) => {
        this.isMatching = false;
        this.toastService.error(err.error?.detail || 'Matching failed');
      },
    });
  }

  /** Clear frontend results and form fields only. */
  clearResults(): void {
    this.matchResults = [];
    this.jobDescription = '';
    if (this.jobComponent) {
      this.jobComponent.jobDescription.reset();
    }
  }

  /** Clear all data from both frontend and backend. */
  clearAll(): void {
    this.apiService.clearAll().subscribe({
      next: () => {
        this.matchResults = [];
        this.jobDescription = '';
        
        // Force clear the upload component's file lists
        if (this.uploadComponent) {
          this.uploadComponent.uploadedFileNames = [];
          this.uploadComponent.files = [];
        }
        
        // Force clear the job description text box
        if (this.jobComponent) {
          this.jobComponent.jobDescription.reset();
        }
        
        this.toastService.success('All data cleared');
      },
      error: (err) => {
        this.toastService.error(err.error?.detail || 'Clear failed');
      },
    });
  }
}