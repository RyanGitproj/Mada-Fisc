import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, of } from 'rxjs';

import { LoginRequest, LoginResponse } from '../models/api-response.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly TOKEN_KEY = 'mada_fisc_access_token';
  private readonly REFRESH_KEY = 'mada_fisc_refresh_token';
  private readonly USER_KEY = 'mada_fisc_user';

  /** Signal réactif pour l'état d'authentification */
  readonly isAuthenticated = signal<boolean>(this.hasToken());
  readonly currentUser = signal<LoginResponse['user'] | null>(this.getStoredUser());
  readonly username = computed(() => this.currentUser()?.username ?? '');

  constructor(private http: HttpClient) {}

  /**
   * Authentifier un utilisateur.
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/auth/login/`, credentials).pipe(
      tap((response) => {
        localStorage.setItem(this.TOKEN_KEY, response.access);
        localStorage.setItem(this.REFRESH_KEY, response.refresh);
        localStorage.setItem(this.USER_KEY, JSON.stringify(response.user));
        this.isAuthenticated.set(true);
        this.currentUser.set(response.user);
      })
    );
  }

  /**
   * Rafraîchir le token d'accès.
   */
  refresh(): Observable<{ access: string; refresh: string }> {
    const refreshToken = localStorage.getItem(this.REFRESH_KEY);
    if (!refreshToken) {
      this.logout();
      return of() as unknown as Observable<{ access: string; refresh: string }>;
    }

    return this.http
      .post<{ access: string; refresh: string }>(`${environment.apiUrl}/auth/refresh/`, {
        refresh: refreshToken,
      })
      .pipe(
        tap((response) => {
          localStorage.setItem(this.TOKEN_KEY, response.access);
          localStorage.setItem(this.REFRESH_KEY, response.refresh);
        })
      );
  }

  /**
   * Déconnecter l'utilisateur.
   */
  logout(): void {
    const refreshToken = localStorage.getItem(this.REFRESH_KEY);
    if (refreshToken) {
      this.http.post(`${environment.apiUrl}/auth/logout/`, { refresh: refreshToken }).subscribe({
        complete: () => this.clearStorage(),
        error: () => this.clearStorage(),
      });
    } else {
      this.clearStorage();
    }
  }

  /**
   * Récupérer le token d'accès.
   */
  getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Récupérer le token de rafraîchissement.
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  private clearStorage(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }

  private getStoredUser(): LoginResponse['user'] | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }
}
