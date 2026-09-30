import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'cl-shell',
  imports: [RouterOutlet, RouterLink],
  template: `
    <div class="shell">
      <header class="shell__header">
        <a routerLink="/dashboard" class="shell__brand">
          <svg class="shell__mark" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="9" />
            <path d="M12,8 L15.8,10.76 L14.35,15.24 L9.65,15.24 L8.2,10.76 Z" />
            <path d="M12,8 L12,3 M15.8,10.76 L20.56,9.22 M14.35,15.24 L17.29,19.28 M9.65,15.24 L6.71,19.28 M8.2,10.76 L3.44,9.22" />
          </svg>
          COMPET LAB
        </a>
        <div class="shell__user">
          @if (auth.currentUser(); as user) {
            <span class="shell__email">{{ user.email }}</span>
            <span class="badge ok">{{ user.role }}</span>
            <button (click)="logout()">Déconnexion</button>
          }
        </div>
      </header>
      <main class="shell__content">
        <router-outlet />
      </main>
    </div>
  `,
  styles: [
    `
      .shell { min-height: 100%; display: flex; flex-direction: column; }
      .shell__header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.9rem 1.5rem; border-bottom: 1px solid var(--cl-color-border);
        border-top: 2px solid var(--cl-color-accent);
        background: var(--cl-color-surface);
      }
      .shell__brand { display: flex; align-items: center; gap: 0.45rem; color: var(--cl-color-accent); font-weight: 700; letter-spacing: 0.04em; text-decoration: none; }
      .shell__mark { width: 18px; height: 18px; flex-shrink: 0; fill: none; stroke: currentColor; stroke-width: 1.3; stroke-linejoin: round; }
      .shell__user { display: flex; align-items: center; gap: 0.6rem; }
      .shell__email { color: var(--cl-color-text-muted); font-size: 0.85rem; }
      .shell__content { flex: 1; padding: 1.5rem; max-width: 1100px; width: 100%; margin: 0 auto; }
    `,
  ],
})
export class ShellComponent {
  protected readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
