import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

@Component({
  selector: 'app-breadcrumb',
  standalone: true,
  imports: [RouterLink, NgFor, NgIf],
  template: `
    <nav class="mb-4">
      <ol class="flex items-center space-x-2 text-sm text-gray-500">
        <li *ngFor="let item of items; let last = last" class="flex items-center">
          <a *ngIf="item.path && !last"
             [routerLink]="item.path"
             class="hover:text-primary-600 transition-colors">
            {{ item.label }}
          </a>
          <span *ngIf="last" class="text-gray-900 font-medium">{{ item.label }}</span>
          <svg *ngIf="!last" class="w-4 h-4 mx-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </li>
      </ol>
    </nav>
  `,
})
export class BreadcrumbComponent {
  @Input() items: BreadcrumbItem[] = [];
}
