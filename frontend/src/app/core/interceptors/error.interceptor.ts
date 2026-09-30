import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { ProblemDetails } from '../models';
import { AuthService } from '../services/auth.service';

/**
 * Normalizes backend errors (application/problem+json, RFC 7807) into a
 * consistent shape and centralizes the "session expired" redirect, so
 * feature components only ever have to deal with a plain message string.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse) {
        if (error.status === 401 && !req.url.includes('/auth/login')) {
          auth.logout();
          router.navigate(['/login']);
        }

        const problem = error.error as Partial<ProblemDetails> | undefined;
        const message = problem?.detail ?? error.message ?? 'Une erreur inattendue est survenue.';
        return throwError(() => new Error(message));
      }
      return throwError(() => error);
    }),
  );
};
