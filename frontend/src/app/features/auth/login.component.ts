import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { ErrorHandlerService } from '../../core/services/error-handler.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <div>
          <h1 class="text-center text-3xl font-extrabold text-primary-800">MadaFisc Auto</h1>
          <p class="mt-2 text-center text-sm text-gray-600">Paie & Facturation pour PME Madagascar</p>
        </div>
        <form class="mt-8 space-y-6" (ngSubmit)="onSubmit()">
          @if (errorMessage) {
            <div class="rounded-md bg-red-50 p-4">
              <p class="text-sm text-red-700">{{ errorMessage }}</p>
            </div>
          }
          <div class="rounded-md shadow-sm -space-y-px">
            <div>
              <label for="username" class="sr-only">Nom d'utilisateur</label>
              <input id="username" name="username" type="text"
                     [(ngModel)]="username" required
                     class="input-field rounded-t-md rounded-b-none"
                     placeholder="Nom d'utilisateur">
            </div>
            <div>
              <label for="password" class="sr-only">Mot de passe</label>
              <input id="password" name="password" type="password"
                     [(ngModel)]="password" required
                     class="input-field rounded-t-none rounded-b-md"
                     placeholder="Mot de passe">
            </div>
          </div>
          <div>
            <button type="submit" [disabled]="loading"
                    class="btn-primary w-full flex justify-center">
              @if (loading) {
                <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Connexion...
              } @else {
                Se connecter
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
})
export class LoginComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private errorHandler = inject(ErrorHandlerService);

  username = '';
  password = '';
  loading = false;
  errorMessage = '';

  onSubmit(): void {
    this.errorMessage = '';
    this.loading = true;

    this.authService.login({ username: this.username, password: this.password }).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = this.errorHandler.handle(err);
      },
    });
  }
}
