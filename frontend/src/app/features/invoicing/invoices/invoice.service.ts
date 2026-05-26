import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Invoice, InvoiceCreateRequest, PaginatedResponse } from '../../../core/models/api-response.model';
import { environment } from '../../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class InvoiceService {
  private http = inject(HttpClient);

  getInvoices(params?: Record<string, string>): Observable<PaginatedResponse<Invoice>> {
    return this.http.get<PaginatedResponse<Invoice>>(`${environment.apiUrl}/invoicing/invoices/`, { params });
  }

  getInvoice(id: number): Observable<Invoice> {
    return this.http.get<Invoice>(`${environment.apiUrl}/invoicing/invoices/${id}/`);
  }

  createInvoice(data: InvoiceCreateRequest): Observable<Invoice> {
    return this.http.post<Invoice>(`${environment.apiUrl}/invoicing/invoices/`, data);
  }

  changeStatus(id: number, status: string): Observable<Invoice> {
    return this.http.patch<Invoice>(`${environment.apiUrl}/invoicing/invoices/${id}/status/`, { status });
  }

  getPdfUrl(invoiceId: number): string {
    return `${environment.apiUrl}/invoicing/invoices/${invoiceId}/pdf/`;
  }
}
