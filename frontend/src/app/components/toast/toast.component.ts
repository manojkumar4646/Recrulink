import { Component } from '@angular/core';
import { ToastService, Toast } from '../../services/toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  template: `
    <div class="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm">
      @for (toast of toastService.toasts; track toast.id) {
        <div
          (click)="toastService.remove(toast.id)"
          class="flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg cursor-pointer
                 transition-all duration-300 animate-slide-in"
          [class]="getToastClasses(toast.type)"
        >
          <span class="text-lg">{{ getToastIcon(toast.type) }}</span>
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      }
    </div>
  `,
  styles: [`
    :host {
      display: contents;
    }
    @keyframes slide-in {
      from { opacity: 0; transform: translateX(100px); }
      to   { opacity: 1; transform: translateX(0); }
    }
    .animate-slide-in {
      animation: slide-in 0.3s ease-out;
    }
  `],
})
export class ToastComponent {
  constructor(public toastService: ToastService) {}

  getToastClasses(type: Toast['type']): string {
    switch (type) {
      case 'success': return 'bg-emerald-50 text-emerald-800 border border-emerald-200';
      case 'error':   return 'bg-red-50 text-red-800 border border-red-200';
      case 'info':    return 'bg-blue-50 text-blue-800 border border-blue-200';
      default:        return 'bg-slate-50 text-slate-800 border border-slate-200';
    }
  }

  getToastIcon(type: Toast['type']): string {
    switch (type) {
      case 'success': return '✓';
      case 'error':   return '✕';
      case 'info':    return 'ℹ';
      default:        return '•';
    }
  }
}