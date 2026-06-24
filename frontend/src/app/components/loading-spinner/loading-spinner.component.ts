import { Component } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  template: `
    <div class="flex flex-col items-center justify-center py-12 gap-3">
      <div class="relative w-10 h-10">
        <div class="absolute inset-0 rounded-full border-[3px] border-slate-200"></div>
        <div class="absolute inset-0 rounded-full border-[3px] border-transparent border-t-brand-500 animate-spin"></div>
      </div>
      <p class="text-sm text-slate-500 font-medium">Processing...</p>
    </div>
  `,
})
export class LoadingSpinnerComponent {}