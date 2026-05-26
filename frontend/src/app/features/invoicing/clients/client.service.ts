import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Client, PaginatedResponse } from '../../../core/models/api-response.model';
import { environment } from '../../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ClientService {
  private http = inject(HttpClient);

  getClients(params?: Record<string, string>): Observable<PaginatedResponse<Client>> {
    return this.http.get<PaginatedResponse<Client>>(`${environment.apiUrl}/invoicing/clients/`, { params });
  }

  getClient(id: number): Observable<Client> {
    return this.http.get<Client>(`${environment.apiUrl}/invoicing/clients/${id}/`);
  }

  createClient(data: Partial<Client>): Observable<Client> {
    return this.http.post<Client>(`${environment.apiUrl}/invoicing/clients/`, data);
  }

  updateClient(id: number, data: Partial<Client>): Observable<Client> {
    return this.http.put<Client>(`${environment.apiUrl}/invoicing/clients/${id}/`, data);
  }

  deleteClient(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/invoicing/clients/${id}/`);
  }
}
