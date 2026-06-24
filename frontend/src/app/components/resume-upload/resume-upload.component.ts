import { Component, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ToastService } from '../../services/toast.service';
import { LoadingSpinnerComponent } from '../loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-resume-upload',
  standalone: true,
  imports: [FormsModule, LoadingSpinnerComponent],
  templateUrl: './resume-upload.component.html',
})
export class ResumeUploadComponent {
  @Output() uploaded = new EventEmitter<string[]>();

  files: File[] = [];
  uploadedFileNames: string[] = [];
  isDragging = false;
  isLoading = false;

  constructor(
    private apiService: ApiService,
    private toastService: ToastService,
  ) {}

  /** Handle files selected via the file input. */
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.addFiles(Array.from(input.files));
    }
  }

  /** Handle files dropped onto the drag-and-drop zone. */
  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    if (event.dataTransfer?.files) {
      this.addFiles(Array.from(event.dataTransfer.files));
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(): void {
    this.isDragging = false;
  }

  /** Add files to the list, filtering for PDF and DOCX only. */
  private addFiles(newFiles: File[]): void {
    const allowed = ['.pdf', '.docx', '.doc'];
    for (const file of newFiles) {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (allowed.includes(ext)) {
        // Prevent duplicates
        if (!this.files.some(f => f.name === file.name && f.size === file.size)) {
          this.files.push(file);
        }
      } else {
        this.toastService.error(`Unsupported file: ${file.name}`);
      }
    }
  }

  /** Remove a file from the pending list. */
  removeFile(index: number): void {
    this.files.splice(index, 1);
  }

  /** Upload all pending files to the backend. */
  uploadFiles(): void {
    if (this.files.length === 0) {
      this.toastService.error('Please select at least one file');
      return;
    }

    this.isLoading = true;
    this.apiService.uploadResumes(this.files).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.uploadedFileNames = [...this.uploadedFileNames, ...response.filenames];
        this.files = [];
        this.toastService.success(response.message);
        this.uploaded.emit(response.filenames);
      },
      error: (err) => {
        this.isLoading = false;
        this.toastService.error(err.error?.detail || 'Upload failed');
      },
    });
  }

  /** Format file size for display. */
  formatSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }
}