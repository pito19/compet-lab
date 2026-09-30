import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthenticatedUser, LoginResponse, Role } from '../models';

const STORAGE_KEY = 'compet_lab_auth';

interface StoredAuth {
  token: string;
  email: string;
  role: Role;
}

/**
 * Owns the authentication state for the whole application.
 *
 * The token is kept in localStorage for simplicity in this prototype.
 * In a production deployment, this would typically be replaced by an
 * httpOnly cookie issued by a backend session/BFF layer to mitigate
 * XSS token theft -- a deliberate simplification, not an oversight.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  private readonly stored = this.readStored();
  private readonly _user = signal<AuthenticatedUser | null>(
    this.stored ? { email: this.stored.email, role: this.stored.role } : null,
  );
  private readonly _token = signal<string | null>(this.stored?.token ?? null);

  readonly currentUser = this._user.asReadonly();
  readonly isAuthenticated = computed(() => this._user() !== null);
  readonly role = computed(() => this._user()?.role ?? null);

  login(email: string, password: string): Observable<LoginResponse> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    return this.http
      .post<LoginResponse>(`${environment.apiBaseUrl}/auth/login`, body.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(
        tap((response) => {
          const stored: StoredAuth = { token: response.access_token, email: response.email, role: response.role };
          localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
          this._token.set(stored.token);
          this._user.set({ email: stored.email, role: stored.role });
        }),
      );
  }

  logout(): void {
    localStorage.removeItem(STORAGE_KEY);
    this._token.set(null);
    this._user.set(null);
  }

  getToken(): string | null {
    return this._token();
  }

  hasAnyRole(...roles: Role[]): boolean {
    const current = this.role();
    return current !== null && roles.includes(current);
  }

  private readStored(): StoredAuth | null {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as StoredAuth;
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  }
}
