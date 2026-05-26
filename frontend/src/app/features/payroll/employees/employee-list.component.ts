import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { EmployeeService } from './employee.service';
import { Employee } from '../../../core/models/api-response.model';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';
import { CurrencyMgaPipe } from '../../../shared/pipes/currency-mga.pipe';

@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [CommonModule, RouterLink, CurrencyMgaPipe],
  template: `
    <div class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Employés</h2>
        <a routerLink="/payroll/employees/new" class="btn-primary">
          + Nouvel employé
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
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">Nom</th>
                  <th class="text-left text-xs font-medium text-gray-500 uppercase py-3 px-4">E-mail</th>
                  <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">Salaire de base</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Org. sanitaire</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Personnes à charge</th>
                  <th class="text-center text-xs font-medium text-gray-500 uppercase py-3 px-4">Statut</th>
                  <th class="text-right text-xs font-medium text-gray-500 uppercase py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                @for (emp of employees(); track emp.id) {
                  <tr class="border-b border-gray-100 hover:bg-gray-50">
                    <td class="py-3 px-4 text-sm font-medium">{{ emp.full_name }}</td>
                    <td class="py-3 px-4 text-sm text-gray-500">{{ emp.email }}</td>
                    <td class="py-3 px-4 text-sm text-right">{{ emp.base_salary | currencyMga }}</td>
                    <td class="py-3 px-4 text-sm text-center">{{ emp.organism_sanitaire }}</td>
                    <td class="py-3 px-4 text-sm text-center">{{ emp.dependants_count }}</td>
                    <td class="py-3 px-4 text-center">
                      @if (emp.is_active) {
                        <span class="badge-success">Actif</span>
                      } @else {
                        <span class="badge-danger">Inactif</span>
                      }
                    </td>
                    <td class="py-3 px-4 text-right">
                      <a [routerLink]="['/payroll/employees', emp.id, 'edit']"
                         class="text-primary-600 hover:text-primary-800 text-sm font-medium">
                        Modifier
                      </a>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="7" class="py-8 text-center text-gray-400">Aucun employé trouvé.</td>
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
export class EmployeeListComponent implements OnInit {
  private employeeService = inject(EmployeeService);
  private errorHandler = inject(ErrorHandlerService);

  employees = signal<Employee[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.employeeService.getEmployees().subscribe({
      next: (response) => {
        this.employees.set(response.results);
        this.loading.set(false);
      },
      error: (err) => {
        this.errorHandler.handle(err);
        this.loading.set(false);
      },
    });
  }
}
