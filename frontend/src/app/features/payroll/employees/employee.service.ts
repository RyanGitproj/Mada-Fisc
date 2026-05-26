import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Employee, PaginatedResponse, PayslipGenerateRequest, PayslipGenerateResponse } from '../../../core/models/api-response.model';
import { environment } from '../../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class EmployeeService {
  private http = inject(HttpClient);

  getEmployees(params?: Record<string, string>): Observable<PaginatedResponse<Employee>> {
    return this.http.get<PaginatedResponse<Employee>>(`${environment.apiUrl}/payroll/employees/`, { params });
  }

  getEmployee(id: number): Observable<Employee> {
    return this.http.get<Employee>(`${environment.apiUrl}/payroll/employees/${id}/`);
  }

  createEmployee(data: Partial<Employee>): Observable<Employee> {
    return this.http.post<Employee>(`${environment.apiUrl}/payroll/employees/`, data);
  }

  updateEmployee(id: number, data: Partial<Employee>): Observable<Employee> {
    return this.http.put<Employee>(`${environment.apiUrl}/payroll/employees/${id}/`, data);
  }

  deleteEmployee(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/payroll/employees/${id}/`);
  }
}
