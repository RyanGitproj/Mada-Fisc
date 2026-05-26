import { Routes } from '@angular/router';
import { AuthGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard],
  },
  {
    path: 'payroll',
    canActivate: [AuthGuard],
    children: [
      {
        path: '',
        redirectTo: 'employees',
        pathMatch: 'full',
      },
      {
        path: 'employees',
        loadComponent: () => import('./features/payroll/employees/employee-list.component').then(m => m.EmployeeListComponent),
      },
      {
        path: 'employees/new',
        loadComponent: () => import('./features/payroll/employees/employee-form.component').then(m => m.EmployeeFormComponent),
      },
      {
        path: 'employees/:id/edit',
        loadComponent: () => import('./features/payroll/employees/employee-form.component').then(m => m.EmployeeFormComponent),
      },
      {
        path: 'payslips',
        loadComponent: () => import('./features/payroll/payslips/payslip-list.component').then(m => m.PayslipListComponent),
      },
    ],
  },
  {
    path: 'invoicing',
    canActivate: [AuthGuard],
    children: [
      {
        path: '',
        redirectTo: 'clients',
        pathMatch: 'full',
      },
      {
        path: 'clients',
        loadComponent: () => import('./features/invoicing/clients/client-list.component').then(m => m.ClientListComponent),
      },
      {
        path: 'clients/new',
        loadComponent: () => import('./features/invoicing/clients/client-form.component').then(m => m.ClientFormComponent),
      },
      {
        path: 'invoices',
        loadComponent: () => import('./features/invoicing/invoices/invoice-list.component').then(m => m.InvoiceListComponent),
      },
      {
        path: 'invoices/new',
        loadComponent: () => import('./features/invoicing/invoices/invoice-form.component').then(m => m.InvoiceFormComponent),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];
