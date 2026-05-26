import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Payslip, PayslipGenerateRequest, PayslipGenerateResponse, MonthlySummary, PaginatedResponse } from '../../../core/models/api-response.model';
import { environment } from '../../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PayslipService {
  private http = inject(HttpClient);

  getPayslips(params?: Record<string, string>): Observable<PaginatedResponse<Payslip>> {
    return this.http.get<PaginatedResponse<Payslip>>(`${environment.apiUrl}/payroll/payslips/`, { params });
  }

  generatePayslip(data: PayslipGenerateRequest): Observable<PayslipGenerateResponse> {
    return this.http.post<PayslipGenerateResponse>(`${environment.apiUrl}/payroll/payslips/generate/`, data);
  }

  generateBatch(month: number, year: number): Observable<{ message: string; count: number }> {
    return this.http.post<{ message: string; count: number }>(`${environment.apiUrl}/payroll/payslips/generate-batch/`, { month, year });
  }

  getMonthlySummary(month: number, year: number): Observable<MonthlySummary> {
    return this.http.get<MonthlySummary>(`${environment.apiUrl}/payroll/payslips/monthly-summary/`, {
      params: { month: String(month), year: String(year) },
    });
  }

  getPdfUrl(payslipId: number): string {
    return `${environment.apiUrl}/payroll/payslips/${payslipId}/pdf/`;
  }
}
