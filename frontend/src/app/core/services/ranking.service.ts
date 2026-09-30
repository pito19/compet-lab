import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Standing } from '../models';

@Injectable({ providedIn: 'root' })
export class RankingService {
  private readonly http = inject(HttpClient);

  getStandings(poolId: string): Observable<Standing[]> {
    return this.http.get<Standing[]>(`${environment.apiBaseUrl}/pools/${poolId}/standings`);
  }
}
