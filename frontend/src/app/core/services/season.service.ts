import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Season } from '../models';

@Injectable({ providedIn: 'root' })
export class SeasonService {
  private readonly http = inject(HttpClient);

  list(): Observable<Season[]> {
    return this.http.get<Season[]>(`${environment.apiBaseUrl}/seasons`);
  }
}
