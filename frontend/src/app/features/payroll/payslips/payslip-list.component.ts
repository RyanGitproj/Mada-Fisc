import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PayslipService } from './payslip.service';
import { Payslip, PayslipGenerateRequest } from '../../../core/models/api-response.model';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';
import { CurrencyMgaPipe } from '../../../shared/pipes/currency-mga.pipe';
import { EmployeeService } from '../employees/employee.service';
import { Employee } from '../../../core/models/api-response.model';

@Component({
  selector: 'app-payslip-list',
  standalone: true,
  imports: [CommonModule, FormsModule, CurrencyMgaPipe],
  template: `
    <div class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Bulletins de paie</h2>
      </div>

      <!-- Formulaire de génération -->
      <div class="card mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Générer un bulletin</h3>
        <div class="flex items-end gap-4">
          <div class="flex-1">
            <label for="employee" class="label-field">Employé</label>
            <select id="employee" [(ngModel)]="generateRequest.employee_id" class="input-field">
              <option [ngValue]="0" disabled>Sélectionner un employé</option>
              @for (emp of employees(); track emp.id) {
                <option [ngValue]="emp.id">{{ emp.full_name }}</option>
              }
            </select>
          </div>
          <div class="w-24">
            <label for="month" class="label-field">Mois</label>
            <select id="month" [(ngModel)]="generateRequest.month" class="input-field">
              @for (m of months; track m.value) {
                <option [ngValue]="m.value">{{ m.label }}</option>
              }
            </select>
          </div>
          <div class="w-28">
            <label for="year" class="label-field">Année</label>
            <input id="year" type="number" [(ngModel)]="generateRequest.year" class="input-field" />
          </div>
          <button (click)="onGenerate()" [disabled]="generating()" class="btn-primary">
            @if (generating()) { Génération... } @else { Générer }
          </button>
        </div>
        @if (generateMessage()) {
          <div class="mt-3 p-3 rounded-md" [class]="generateSuccess() ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
            <p class="text-sm">{{ generateMessage() }}</p>
          </div>
        }
      </div>

      <!-- Liste des bulletins -->
      <div class="card">
        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">Employé</th>
                <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Période</th>
                <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">Brut</th>
                <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">CNaPS</th>
                <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">OSTIE</th>
                <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">FMFP</th>
                <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">IRSA</th>
                <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">Net</th>
                <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">PDF</th>
              </tr>
            </thead>
            <tbody>
              @for (ps of payslips(); track ps.id) {
                <tr class="border-b border-gray-100 hover:bg-gray-50">
                  <td class="py-3 px-4 text-sm font-medium">{{ ps.employee_name }}</td>
                  <td class="py-3 px-4 text-sm text-center">{{ ps.month | number:'2.0' }}/{{ ps.year }}</td>
                  <td class="py-3 px-4 text-sm text-right">{{ ps.gross_salary | currencyMga }}</td>
                  <td class="py-3 px-4 text-sm text-right text-red-600">-{{ ps.cnaps_deduction | currencyMga }}</td>
                  <td class="py-3 px-4 text-sm text-right text-red-600">-{{ ps.ostie_deduction | currencyMga }}</td>
                  <td class="py-3 px-4 text-sm text-right text-red-600">-{{ ps.fmfp_deduction | currencyMga }}</td>
                  <td class="py-3 px-4 text-sm text-right text-red-600">-{{ ps.irsa_tax | currencyMga }}</td>
                  <td class="py-3 px-4 text-sm text-right font-bold text-green-700">{{ ps.net_salary | currencyMga }}</td>
                  <td class="py-3 px-4 text-center">
                    <button (click)="downloadPdf(ps.id)" class="text-primary-600 hover:text-primary-800 text-sm">
                      PDF
                    </button>
                  </td>
                </tr>
              } @empty {
                <tr>
                  <td colspan="9" class="py-8 text-center text-gray-400">Aucun bulletin trouvé.</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
})
export class PayslipListComponent implements OnInit {
  private payslipService = inject(PayslipService);
  private employeeService = inject(EmployeeService);
  private errorHandler = inject(ErrorHandlerService);

  payslips = signal<Payslip[]>([]);
  employees = signal<Employee[]>([]);
  loading = signal(true);
  generating = signal(false);
  generateMessage = signal('');
  generateSuccess = signal(false);

  generateRequest: PayslipGenerateRequest = { employee_id: 0, month: 1, year: new Date().getFullYear() };

  months = [
    { value: 1, label: 'Janvier' }, { value: 2, label: 'Février' },
    { value: 3, label: 'Mars' }, { value: 4, label: 'Avril' },
    { value: 5, label: 'Mai' }, { value: 6, label: 'Juin' },
    { value: 7, label: 'Juillet' }, { value: 8, label: 'Août' },
    { value: 9, label: 'Septembre' }, { value: 10, label: 'Octobre' },
    { value: 11, label: 'Novembre' }, { value: 12, label: 'Décembre' },
  ];

  ngOnInit(): void {
    this.loadEmployees();
    this.loadPayslips();
  }

  loadEmployees(): void {
    this.employeeService.getEmployees({ is_active: 'true' }).subscribe({
      next: (res) => this.employees.set(res.results),
      error: (err) => this.errorHandler.handle(err),
    });
  }

  loadPayslips(): void {
    this.payslipService.getPayslips().subscribe({
      next: (res) => {
        this.payslips.set(res.results);
        this.loading.set(false);
      },
      error: (err) => {
        this.errorHandler.handle(err);
        this.loading.set(false);
      },
    });
  }

  onGenerate(): void {
    if (this.generateRequest.employee_id === 0) return;
    this.generating.set(true);
    this.generateMessage.set('');

    this.payslipService.generatePayslip(this.generateRequest).subscribe({
      next: (response) => {
        this.generateMessage.set(response.message);
        this.generateSuccess.set(true);
        this.generating.set(false);
        this.loadPayslips();
      },
      error: (err) => {
        this.generateMessage.set(this.errorHandler.handle(err));
        this.generateSuccess.set(false);
        this.generating.set(false);
      },
    });
  }

  downloadPdf(payslipId: number): void {
    const url = this.payslipService.getPdfUrl(payslipId);
    window.open(url, '_blank');
  }
}
