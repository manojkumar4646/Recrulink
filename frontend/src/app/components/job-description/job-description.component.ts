import { Component, Output, EventEmitter } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-job-description',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './job-description.component.html',
})
export class JobDescriptionComponent {
  @Output() submitted = new EventEmitter<string>();

  jobDescription = new FormControl('', { nonNullable: true });

  /** Emit the job description text when the user submits. */
  onSubmit(): void {
    const value = this.jobDescription.value.trim();
    if (!value) return;
    this.submitted.emit(value);
  }
}