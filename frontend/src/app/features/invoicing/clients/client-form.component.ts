import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ClientService } from './client.service';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';

@Component({
  selector: 'app-client-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="p-6 max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Nouveau client</h2>

      @if (errorMessage()) {
        <div class="rounded-md bg-red-50 p-4 mb-4">
          <p class="text-sm text-red-700">{{ errorMessage() }}</p>
        </div>
      }

      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="space-y-4">
        <div>
          <label for="company_name" class="label-field">Raison sociale *</label>
          <input id="company_name" formControlName="company_name" class="input-field" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="nif" class="label-field">NIF</label>
            <input id="nif" formControlName="nif" class="input-field" />
          </div>
          <div>
            <label for="stat" class="label-field">STAT</label>
            <input id="stat" formControlName="stat" class="input-field" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="email" class="label-field">Adresse e-mail</label>
            <input id="email" formControlName="email" type="email" class="input-field" />
          </div>
          <div>
            <label for="phone" class="label-field">Téléphone</label>
            <input id="phone" formControlName="phone" class="input-field" />
          </div>
        </div>

        <div>
          <label for="address" class="label-field">Adresse</label>
          <textarea id="address" formControlName="address" rows="3" class="input-field"></textarea>
        </div>

        <div class="flex items-center gap-4 pt-4">
          <button type="submit" [disabled]="form.invalid || submitting()" class="btn-primary">
            @if (submitting()) { Création... } @else { Créer le client }
          </button>
          <button type="button" (click)="router.navigate(['/invoicing/clients'])" class="btn-secondary">
            Annuler
          </button>
        </div>
      </form>
    </div>
  `,
})
export class ClientFormComponent {
  private clientService = inject(ClientService);
  private errorHandler = inject(ErrorHandlerService);
  private fb = inject(FormBuilder);

  router = inject(Router);
  submitting = signal(false);
  errorMessage = signal('');

  form = this.fb.group({
    company_name: ['', Validators.required],
    nif: [''],
    stat: [''],
    email: [''],
    phone: [''],
    address: [''],
    is_active: [true],
  });

  onSubmit(): void {
    if (this.form.invalid) return;
    this.submitting.set(true);
    this.errorMessage.set('');

    this.clientService.createClient(this.form.value as any).subscribe({
      next: () => this.router.navigate(['/invoicing/clients']),
      error: (err) => {
        this.errorMessage.set(this.errorHandler.handle(err));
        this.submitting.set(false);
      },
    });
  }
}
