import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ClientService } from './client.service';
import { Client } from '../../../core/models/api-response.model';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';

@Component({
  selector: 'app-client-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Clients</h2>
        <button (click)="router.navigate(['/invoicing/clients/new'])" class="btn-primary">
          Ajouter un client
        </button>
      </div>

      @if (loading()) {
        <div class="flex justify-center py-12">
          <svg class="animate-spin h-8 w-8 text-primary-600" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
        </div>
      } @else {
        <div class="card mb-4">
          <p class="text-sm text-gray-500">
            <span class="font-semibold text-gray-900">{{ clients().length }}</span> client(s) total
          </p>
        </div>
        <div class="card">
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">Raison sociale</th>
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">NIF</th>
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">STAT</th>
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">E-mail</th>
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">Téléphone</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Statut</th>
                </tr>
              </thead>
              <tbody>
                @for (cl of clients(); track cl.id) {
                  <tr class="border-b border-gray-100 hover:bg-gray-50">
                    <td class="py-3 px-4 text-sm font-medium">{{ cl.company_name }}</td>
                    <td class="py-3 px-4 text-sm text-gray-500">{{ cl.nif || '—' }}</td>
                    <td class="py-3 px-4 text-sm text-gray-500">{{ cl.stat || '—' }}</td>
                    <td class="py-3 px-4 text-sm text-gray-500">{{ cl.email || '—' }}</td>
                    <td class="py-3 px-4 text-sm text-gray-500">{{ cl.phone || '—' }}</td>
                    <td class="py-3 px-4 text-center">
                      @if (cl.is_active) {
                        <span class="badge-success">Actif</span>
                      } @else {
                        <span class="badge-danger">Inactif</span>
                      }
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="6" class="py-8 text-center text-gray-400">Aucun client trouvé.</td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>
      }
    </div>
  `,
})
export class ClientListComponent implements OnInit {
  private clientService = inject(ClientService);
  private errorHandler = inject(ErrorHandlerService);
  router = inject(Router);

  clients = signal<Client[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.clientService.getClients().subscribe({
      next: (response) => {
        this.clients.set(response.results);
        this.loading.set(false);
      },
      error: (err) => {
        this.errorHandler.handle(err);
        this.loading.set(false);
      },
    });
  }
}
