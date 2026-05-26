import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { EmployeeService } from './employee.service';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';

@Component({
  selector: 'app-employee-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="p-6 max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ isEditing() ? 'Modifier l\'employé' : 'Nouvel employé' }}</h2>

      @if (errorMessage()) {
        <div class="rounded-md bg-red-50 p-4 mb-4">
          <p class="text-sm text-red-700">{{ errorMessage() }}</p>
        </div>
      }

      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="first_name" class="label-field">Prénom</label>
            <input id="first_name" formControlName="first_name" class="input-field" />
          </div>
          <div>
            <label for="last_name" class="label-field">Nom</label>
            <input id="last_name" formControlName="last_name" class="input-field" />
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

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="base_salary" class="label-field">Salaire de base (Ar)</label>
            <input id="base_salary" formControlName="base_salary" type="number" class="input-field" />
          </div>
          <div>
            <label for="organism_sanitaire" class="label-field">Organisme sanitaire</label>
            <select id="organism_sanitaire" formControlName="organism_sanitaire" class="input-field">
              <option value="OSTIE">OSTIE</option>
              <option value="AMIT">AMIT</option>
              <option value="ESIA">ESIA</option>
              <option value="FUNHECE">FUNHECE</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label for="hire_date" class="label-field">Date d'embauche</label>
            <input id="hire_date" formControlName="hire_date" type="date" class="input-field" />
          </div>
          <div>
            <label for="birth_date" class="label-field">Date de naissance</label>
            <input id="birth_date" formControlName="birth_date" type="date" class="input-field" />
          </div>
          <div>
            <label for="dependants_count" class="label-field">Personnes à charge</label>
            <input id="dependants_count" formControlName="dependants_count" type="number" min="0" class="input-field" />
          </div>
        </div>

        <div>
          <label for="cnaps_number" class="label-field">Numéro CNaPS</label>
          <input id="cnaps_number" formControlName="cnaps_number" class="input-field" />
        </div>

        <div class="flex items-center gap-4 pt-4">
          <button type="submit" [disabled]="form.invalid || submitting()" class="btn-primary">
            @if (submitting()) { Enregistrement... } 
            @else if (isEditing()) { Mettre à jour } 
            @else { Créer l'employé }
          </button>
          <button type="button" (click)="router.navigate(['/payroll/employees'])" class="btn-secondary">
            Annuler
          </button>
        </div>
      </form>
    </div>
  `,
})
export class EmployeeFormComponent {
  private employeeService = inject(EmployeeService);
  private errorHandler = inject(ErrorHandlerService);
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);

  router = inject(Router);
  isEditing = signal(false);
  employeeId = signal<number | null>(null);
  submitting = signal(false);
  errorMessage = signal('');

  form = this.fb.group({
    first_name: ['', Validators.required],
    last_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    phone: [''],
    base_salary: ['', [Validators.required, Validators.min(0)]],
    hire_date: ['', Validators.required],
    birth_date: [''],
    dependants_count: [0, [Validators.required, Validators.min(0)]],
    cnaps_number: [''],
    organism_sanitaire: ['OSTIE'],
    is_active: [true],
  });

  constructor() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditing.set(true);
      this.employeeId.set(Number(id));
      this.employeeService.getEmployee(Number(id)).subscribe({
        next: (emp) => this.form.patchValue(emp),
        error: (err) => this.errorMessage.set(this.errorHandler.handle(err)),
      });
    }
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.submitting.set(true);
    this.errorMessage.set('');

    const request$ = this.isEditing()
      ? this.employeeService.updateEmployee(this.employeeId()!, this.form.value as any)
      : this.employeeService.createEmployee(this.form.value as any);

    request$.subscribe({
      next: () => this.router.navigate(['/payroll/employees']),
      error: (err) => {
        this.errorMessage.set(this.errorHandler.handle(err));
        this.submitting.set(false);
      },
    });
  }
}
