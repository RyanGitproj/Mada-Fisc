import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { InvoiceService } from './invoice.service';
import { Invoice } from '../../../core/models/api-response.model';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';
import { CurrencyMgaPipe } from '../../../shared/pipes/currency-mga.pipe';

@Component({
  selector: 'app-invoice-list',
  standalone: true,
  imports: [CommonModule, RouterLink, CurrencyMgaPipe],
  template: `
    <div class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Factures</h2>
        <a routerLink="/invoicing/invoices/new" class="btn-primary">
          + Nouvelle facture
        </a>
      </div>

      @if (loading()) {
        <div class="flex justify-center py-12">
          <svg class="animate-spin h-8 w-8 text-primary-600" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
        </div>
      } @else {
        <div class="card">
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">Numéro</th>
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">Client</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Émission</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Échéance</th>
                  <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">HT</th>
                  <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">TVA</th>
                  <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">TTC</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Statut</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                @for (inv of invoices(); track inv.id) {
                  <tr class="border-b border-gray-100 hover:bg-gray-50">
                    <td class="py-3 px-4 text-sm font-medium">{{ inv.invoice_number }}</td>
                    <td class="py-3 px-4 text-sm">{{ inv.client_name }}</td>
                    <td class="py-3 px-4 text-sm text-center">{{ inv.issue_date | date:'dd/MM/yyyy' }}</td>
                    <td class="py-3 px-4 text-sm text-center">{{ inv.due_date | date:'dd/MM/yyyy' }}</td>
                    <td class="py-3 px-4 text-sm text-right">{{ inv.amount_ht | currencyMga }}</td>
                    <td class="py-3 px-4 text-sm text-right">{{ inv.tva_amount | currencyMga }}</td>
                    <td class="py-3 px-4 text-sm text-right font-bold">{{ inv.amount_ttc | currencyMga }}</td>
                    <td class="py-3 px-4 text-center">
                      <span [class]="getStatusClass(inv.status)">{{ getStatusLabel(inv.status) }}</span>
                    </td>
                    <td class="py-3 px-4 text-center space-x-2">
                      @if (inv.status === 'DRAFT') {
                        <button (click)="changeStatus(inv.id, 'SENT')" class="text-primary-600 hover:text-primary-800 text-sm font-medium">
                          Envoyer
                        </button>
                      }
                      @if (inv.status === 'SENT' || inv.status === 'OVERDUE') {
                        <button (click)="changeStatus(inv.id, 'PAID')" class="text-green-600 hover:text-green-800 text-sm font-medium">
                          Marquer payée
                        </button>
                      }
                      <button (click)="downloadPdf(inv.id)" class="text-gray-500 hover:text-gray-700 text-sm">
                        PDF
                      </button>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="9" class="py-8 text-center text-gray-400">Aucune facture trouvée.</td>
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
export class InvoiceListComponent implements OnInit {
  private invoiceService = inject(InvoiceService);
  private errorHandler = inject(ErrorHandlerService);

  invoices = signal<Invoice[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.invoiceService.getInvoices().subscribe({
      next: (response) => {
        this.invoices.set(response.results);
        this.loading.set(false);
      },
      error: (err) => {
        this.errorHandler.handle(err);
        this.loading.set(false);
      },
    });
  }

  changeStatus(id: number, status: string): void {
    this.invoiceService.changeStatus(id, status).subscribe({
      next: () => this.ngOnInit(),
      error: (err) => this.errorHandler.handle(err),
    });
  }

  downloadPdf(invoiceId: number): void {
    const url = this.invoiceService.getPdfUrl(invoiceId);
    window.open(url, '_blank');
  }

  getStatusClass(status: string): string {
    const classes: Record<string, string> = {
      DRAFT: 'badge-warning',
      SENT: 'badge-info',
      PAID: 'badge-success',
      OVERDUE: 'badge-danger',
    };
    return classes[status] || 'badge';
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      DRAFT: 'Brouillon',
      SENT: 'Envoyée',
      PAID: 'Payée',
      OVERDUE: 'En retard',
    };
    return labels[status] || status;
  }
}
