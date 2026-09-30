import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Role } from '../models';
import { AuthService } from '../services/auth.service';

/**
 * Factory producing a route guard restricted to the given roles.
 * Usage: canActivate: [roleGuard('ADMIN')]
 */
export function roleGuard(...roles: Role[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (auth.hasAnyRole(...roles)) {
      return true;
    }

    return router.createUrlTree(['/dashboard']);
  };
}
