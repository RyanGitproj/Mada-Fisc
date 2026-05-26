import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InvoiceService } from './invoice.service';
import { ClientService } from '../clients/client.service';
import { Client, InvoiceCreateRequest } from '../../../core/models/api-response.model';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';
import { CurrencyMgaPipe } from '../../../shared/pipes/currency-mga.pipe';

@Component({
  selector: 'app-invoice-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CurrencyMgaPipe],
  template: `
    <div class="p-6 max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Nouvelle facture</h2>

      @if (errorMessage()) {
        <div class="rounded-md bg-red-50 p-4 mb-4">
          <p class="text-sm text-red-700">{{ errorMessage() }}</p>
        </div>
      }

      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="space-y-4">
        <div>
          <label for="client_id" class="label-field">Client</label>
          <select id="client_id" formControlName="client_id" class="input-field">
            <option [ngValue]="0" disabled>Sélectionner un client</option>
            @for (cl of clients(); track cl.id) {
              <option [ngValue]="cl.id">{{ cl.company_name }}</option>
            }
          </select>
        </div>

        <div>
          <label for="amount_ht" class="label-field">Montant HT (Ar)</label>
          <input id="amount_ht" formControlName="amount_ht" type="number" class="input-field" />
        </div>

        <!-- Aperçu TVA -->
        @if (previewTVA() !== null) {
          <div class="bg-gray-50 rounded-lg p-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Montant HT</span>
              <span>{{ previewTVA()!.amount_ht | currencyMga }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">TVA (20%)</span>
              <span>{{ previewTVA()!.tva_amount | currencyMga }}</span>
            </div>
            <div class="flex justify-between text-sm font-bold border-t pt-2">
              <span>Montant TTC</span>
              <span class="text-primary-700">{{ previewTVA()!.amount_ttc | currencyMga }}</span>
            </div>
          </div>
        }

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="issue_date" class="label-field">Date d'émission</label>
            <input id="issue_date" formControlName="issue_date" type="date" class="input-field" />
          </div>
          <div>
            <label for="due_date" class="label-field">Date d'échéance</label>
            <input id="due_date" formControlName="due_date" type="date" class="input-field" />
          </div>
        </div>

        <div>
          <label for="notes" class="label-field">Notes</label>
          <textarea id="notes" formControlName="notes" rows="3" class="input-field"></textarea>
        </div>

        <div class="flex items-center gap-4 pt-4">
          <button type="submit" [disabled]="form.invalid || submitting()" class="btn-primary">
            @if (submitting()) { Création... } @else { Créer la facture }
          </button>
          <button type="button" (click)="router.navigate(['/invoicing/invoices'])" class="btn-secondary">
            Annuler
          </button>
        </div>
      </form>
    </div>
  `,
})
export class InvoiceFormComponent {
  private invoiceService = inject(InvoiceService);
  private clientService = inject(ClientService);
  private errorHandler = inject(ErrorHandlerService);
  private fb = inject(FormBuilder);

  router = inject(Router);
  clients = signal<Client[]>([]);
  submitting = signal(false);
  errorMessage = signal('');
  previewTVA = signal<{ amount_ht: string; tva_amount: string; amount_ttc: string } | null>(null);

  form = this.fb.group({
    client_id: [0, Validators.required],
    amount_ht: ['', [Validators.required, Validators.min(0)]],
    issue_date: [new Date().toISOString().split('T')[0]],
    due_date: ['', Validators.required],
    notes: [''],
  });

  constructor() {
    this.loadClients();

    // Calculer l'aperçu TVA en temps réel
    this.form.get('amount_ht')?.valueChanges.subscribe((value) => {
      const amount = parseFloat(value || '0');
      if (!isNaN(amount) && amount > 0) {
        const tva = amount * 0.20;
        this.previewTVA.set({
          amount_ht: amount.toFixed(2),
          tva_amount: tva.toFixed(2),
          amount_ttc: (amount + tva).toFixed(2),
        });
      } else {
        this.previewTVA.set(null);
      }
    });
  }

  loadClients(): void {
    this.clientService.getClients({ is_active: 'true' }).subscribe({
      next: (res) => this.clients.set(res.results),
      error: (err) => this.errorHandler.handle(err),
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.submitting.set(true);
    this.errorMessage.set('');

    const data: InvoiceCreateRequest = {
      client_id: this.form.value.client_id!,
      amount_ht: this.form.value.amount_ht!,
      due_date: this.form.value.due_date!,
      issue_date: this.form.value.issue_date || undefined,
      notes: this.form.value.notes || undefined,
    };

    this.invoiceService.createInvoice(data).subscribe({
      next: () => this.router.navigate(['/invoicing/invoices']),
      error: (err) => {
        this.errorMessage.set(this.errorHandler.handle(err));
        this.submitting.set(false);
      },
    });
  }
}
