import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from './dashboard.service';
import { DashboardSummary } from '../../core/models/api-response.model';
import { ErrorHandlerService } from '../../core/services/error-handler.service';
import { CurrencyMgaPipe } from '../../shared/pipes/currency-mga.pipe';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, CurrencyMgaPipe],
  template: `
    <div class="p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Tableau de bord</h2>
      <p class="text-sm text-gray-500 mb-8">Période : {{ summary()?.periode?.mois }}/{{ summary()?.periode?.annee }}</p>

      @if (loading()) {
        <div class="flex items-center justify-center py-12">
          <svg class="animate-spin h-8 w-8 text-primary-600" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
        </div>
      } @else if (summary()) {
        <!-- Cartes métriques -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div class="card">
            <p class="text-sm font-medium text-gray-500">Masse salariale brute</p>
            <p class="text-2xl font-bold text-gray-900 mt-1">{{ summary()!.payroll.masse_salariale_brute | currencyMga }}</p>
          </div>
          <div class="card">
            <p class="text-sm font-medium text-gray-500">Employés actifs</p>
            <p class="text-2xl font-bold text-primary-700 mt-1">{{ summary()!.payroll.employes_actifs }}</p>
          </div>
          <div class="card">
            <p class="text-sm font-medium text-gray-500">TVA collectée</p>
            <p class="text-2xl font-bold text-green-700 mt-1">{{ summary()!.invoicing.tva_collectee | currencyMga }}</p>
          </div>
          <div class="card">
            <p class="text-sm font-medium text-gray-500">Factures en attente</p>
            <p class="text-2xl font-bold text-yellow-700 mt-1">{{ summary()!.invoicing.factures_en_attente.nombre }}</p>
            <p class="text-sm text-gray-400">{{ summary()!.invoicing.factures_en_attente.montant_ht | currencyMga }} HT</p>
          </div>
        </div>

        <!-- Ligne 2 : IRSA + Retards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div class="card">
            <p class="text-sm font-medium text-gray-500">Total IRSA du mois</p>
            <p class="text-2xl font-bold text-red-700 mt-1">{{ summary()!.payroll.total_irsa | currencyMga }}</p>
            <p class="text-sm text-gray-400">{{ summary()!.payroll.nombre_bulletins }} bulletin(s)</p>
          </div>
          <div class="card border-red-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-500">Factures en retard</p>
                <p class="text-2xl font-bold text-red-700 mt-1">
                  <span class="badge-danger">{{ summary()!.invoicing.factures_en_retard.nombre }}</span>
                </p>
                <p class="text-sm text-red-500 mt-1">{{ summary()!.invoicing.factures_en_retard.montant_ht | currencyMga }} HT</p>
              </div>
              <svg class="w-10 h-10 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Derniers bulletins -->
        <div class="card">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Derniers bulletins générés</h3>
          @if (summary()!.derniers_bulletins.length === 0) {
            <p class="text-gray-400 text-sm">Aucun bulletin généré pour le moment.</p>
          } @else {
            <div class="overflow-x-auto">
              <table class="min-w-full">
                <thead>
                  <tr class="border-b border-gray-200">
                    <th class="text-left text-xs font-medium text-gray-500 uppercase py-2">Employé</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase py-2">Période</th>
                    <th class="text-right text-xs font-medium text-gray-500 uppercase py-2">Salaire net</th>
                  </tr>
                </thead>
                <tbody>
                  @for (ps of summary()!.derniers_bulletins; track ps.id) {
                    <tr class="border-b border-gray-100">
                      <td class="py-2 text-sm">{{ ps.employee_name }}</td>
                      <td class="py-2 text-sm">{{ ps.month | number:'2.0' }}/{{ ps.year }}</td>
                      <td class="py-2 text-sm text-right font-medium">{{ ps.net_salary | currencyMga }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </div>
      }
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  private errorHandler = inject(ErrorHandlerService);

  summary = signal<DashboardSummary | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    this.dashboardService.getSummary().subscribe({
      next: (data) => {
        this.summary.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.errorHandler.handle(err);
        this.loading.set(false);
      },
    });
  }
}
