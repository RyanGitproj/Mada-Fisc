import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { signal } from '@angular/core';

import { ApiErrorResponse } from '../models/api-response.model';

/**
 * Service de gestion centralisée des erreurs.
 */
@Injectable({
  providedIn: 'root',
})
export class ErrorHandlerService {
  /** Signal réactif pour les erreurs globales */
  readonly lastError = signal<ApiErrorResponse | null>(null);

  /**
   * Traiter une erreur HTTP et retourner un message utilisateur.
   */
  handle(error: HttpErrorResponse): string {
    let message = 'Une erreur inattendue est survenue.';

    if (error.status === 0) {
      message = 'Impossible de contacter le serveur. Vérifiez votre connexion.';
    } else if (error.status === 401) {
      message = 'Session expirée. Veuillez vous reconnecter.';
    } else if (error.status === 403) {
      message = 'Vous n\'avez pas les permissions nécessaires.';
    } else if (error.status === 404) {
      message = 'La ressource demandée est introuvable.';
    } else if (error.status === 422 || error.status === 400) {
      const apiError = error.error as ApiErrorResponse;
      if (apiError?.error?.message) {
        message = apiError.error.message;
      }
    } else if (error.status >= 500) {
      message = 'Erreur serveur. Veuillez réessayer plus tard.';
    }

    const apiError = error.error as ApiErrorResponse;
    this.lastError.set(apiError ?? null);

    console.error('[ErrorHandler]', error.status, message, error);
    return message;
  }

  /**
   * Effacer la dernière erreur.
   */
  clear(): void {
    this.lastError.set(null);
  }
}
