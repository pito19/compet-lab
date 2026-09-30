export type Role = 'ADMIN' | 'MANAGER' | 'VIEWER';

export interface AuthenticatedUser {
  email: string;
  role: Role;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: Role;
  email: string;
}

/** Shape of an RFC 7807 (application/problem+json) error response. */
export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  details?: Record<string, unknown>;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
