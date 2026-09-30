import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'cl-login',
  imports: [ReactiveFormsModule],
  template: `
    <div class="login">
      <svg class="login__pitch-mark" viewBox="0 0 800 500" aria-hidden="true">
        <rect x="20" y="20" width="760" height="460" rx="6" />
        <line x1="400" y1="20" x2="400" y2="480" />
        <circle cx="400" cy="250" r="70" />
        <circle cx="400" cy="250" r="2.5" fill="currentColor" stroke="none" />
      </svg>

      <form class="card login__card" [formGroup]="form" (ngSubmit)="submit()">
        <h1 class="login__title">
          <svg class="login__mark" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="9" />
            <path d="M12,8 L15.8,10.76 L14.35,15.24 L9.65,15.24 L8.2,10.76 Z" />
            <path d="M12,8 L12,3 M15.8,10.76 L20.56,9.22 M14.35,15.24 L17.29,19.28 M9.65,15.24 L6.71,19.28 M8.2,10.76 L3.44,9.22" />
          </svg>
          COMPET LAB
        </h1>
        <p class="login__subtitle">Connexion</p>

        @if (errorMessage(); as message) {
          <div class="error-banner">{{ message }}</div>
        }

        <label>
          Email
          <input type="email" formControlName="email" autocomplete="username" />
        </label>

        <label>
          Mot de passe
          <input type="password" formControlName="password" autocomplete="current-password" />
        </label>

        <button type="submit" class="primary" [disabled]="form.invalid || isLoading()">
          {{ isLoading() ? 'Connexion...' : 'Se connecter' }}
        </button>

        <div class="login__hint">
          Comptes de démo : admin&#64;compet-lab.local / Admin123!
        </div>
      </form>
    </div>
  `,
  styles: [
    `
      .login {
        position: relative;
        min-height: 100vh;
        display: flex; align-items: center; justify-content: center;
        overflow: hidden;
      }
      /* Discreet pitch-marking watermark: outline only, very low opacity.*/
      /* The single "this is a football tool" visual cue on this screen.*/
      .login__pitch-mark {
        position: absolute;
        width: min(90vw, 900px);
        color: var(--cl-color-pitch);
        opacity: 0.08;
        fill: none;
        stroke: currentColor;
        stroke-width: 2;
        pointer-events: none;
      }
      .login__card { position: relative; width: 320px; display: flex; flex-direction: column; gap: 0.9rem; }
      .login__title { display: flex; align-items: center; gap: 0.5rem; margin: 0; }
      .login__mark {
        width: 22px; height: 22px; flex-shrink: 0;
        color: var(--cl-color-accent);
        fill: none;
        stroke: currentColor;
        stroke-width: 1.3;
        stroke-linejoin: round;
      }
      .login__subtitle { margin: -0.6rem 0 0; color: var(--cl-color-text-muted); }
      label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.85rem; }
      .login__hint { font-size: 0.75rem; color: var(--cl-color-text-muted); text-align: center; }
    `,
  ],
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly isLoading = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  protected submit(): void {
    if (this.form.invalid) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const { email, password } = this.form.getRawValue();
    this.auth.login(email, password).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (err: Error) => {
        this.isLoading.set(false);
        this.errorMessage.set(err.message || 'Identifiants invalides.');
      },
    });
  }
}
