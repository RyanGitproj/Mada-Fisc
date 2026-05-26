import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <aside class="w-64 bg-primary-800 text-white flex flex-col h-full shadow-lg">
      <!-- Logo / Titre -->
      <div class="px-6 py-4 border-b border-primary-700">
        <h1 class="text-xl font-bold tracking-tight">MadaFisc</h1>
        <p class="text-primary-300 text-xs mt-1">Paie & Facturation PME</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-4 py-6 space-y-1">
        <a routerLink="/dashboard"
           routerLinkActive="bg-primary-900 text-white"
           class="flex items-center px-3 py-2.5 rounded-lg text-primary-100 hover:bg-primary-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          Tableau de bord
        </a>

        <p class="text-xs text-primary-400 uppercase tracking-wider mt-6 mb-2 px-3">Paie</p>
        <a routerLink="/payroll/employees"
           routerLinkActive="bg-primary-900 text-white"
           class="flex items-center px-3 py-2.5 rounded-lg text-primary-100 hover:bg-primary-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
          </svg>
          Employés
        </a>
        <a routerLink="/payroll/payslips"
           routerLinkActive="bg-primary-900 text-white"
           class="flex items-center px-3 py-2.5 rounded-lg text-primary-100 hover:bg-primary-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Bulletins de paie
        </a>

        <p class="text-xs text-primary-400 uppercase tracking-wider mt-6 mb-2 px-3">Facturation</p>
        <a routerLink="/invoicing/clients"
           routerLinkActive="bg-primary-900 text-white"
           class="flex items-center px-3 py-2.5 rounded-lg text-primary-100 hover:bg-primary-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
          Clients
        </a>
        <a routerLink="/invoicing/invoices"
           routerLinkActive="bg-primary-900 text-white"
           class="flex items-center px-3 py-2.5 rounded-lg text-primary-100 hover:bg-primary-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
          Factures
        </a>
      </nav>

      <!-- Utilisateur / Déconnexion -->
      <div class="px-4 py-4 border-t border-primary-700">
        <div class="flex items-center justify-between">
          <div class="text-sm">
            <p class="font-medium text-primary-100">{{ authService.username() || 'Utilisateur' }}</p>
          </div>
          <button (click)="authService.logout()"
                  class="text-primary-300 hover:text-white transition-colors"
                  title="Déconnexion">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  `,
})
export class SidebarComponent {
  readonly authService = inject(AuthService);
}
