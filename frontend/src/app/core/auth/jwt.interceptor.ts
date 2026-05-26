import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, switchMap, throwError, from } from 'rxjs';

import { AuthService } from './auth.service';

/**
 * Intercepteur JWT — injecte le Bearer token et gère le refresh automatique sur 401.
 */
export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Ne pas ajouter le token pour les requêtes d'auth
  if (req.url.includes('/auth/login/') || req.url.includes('/auth/refresh/')) {
    return next(req);
  }

  const token = authService.getAccessToken();
  let authReq = req;

  if (token) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && token) {
        // Tentative de refresh automatique
        return from(authService.refresh()).pipe(
          switchMap((response) => {
            const newReq = req.clone({
              setHeaders: {
                Authorization: `Bearer ${response.access}`,
              },
            });
            return next(newReq);
          }),
          catchError((refreshError) => {
            // Le refresh a échoué → déconnexion
            authService.logout();
            return throwError(() => refreshError);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
