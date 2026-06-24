import { Injectable } from '@angular/core';

/** A single toast notification. */
export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

/**
 * Simple toast notification service.
 * Displays temporary messages at the bottom-right of the screen.
 */
@Injectable({ providedIn: 'root' })
export class ToastService {
  toasts: Toast[] = [];
  private counter = 0;

  /** Show a success toast (green). */
  success(message: string): void {
    this.addToast(message, 'success');
  }

  /** Show an error toast (red). */
  error(message: string): void {
    this.addToast(message, 'error');
  }

  /** Show an info toast (blue). */
  info(message: string): void {
    this.addToast(message, 'info');
  }

  /** Remove a toast by its ID. */
  remove(id: number): void {
    this.toasts = this.toasts.filter(t => t.id !== id);
  }

  private addToast(message: string, type: Toast['type']): void {
    const id = ++this.counter;
    this.toasts.push({ id, message, type });

    // Auto-dismiss after 4 seconds
    setTimeout(() => this.remove(id), 4000);
  }
}