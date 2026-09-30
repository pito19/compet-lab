import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { MatchResult, RecordResultPayload } from '../models';

@Injectable({ providedIn: 'root' })
export class ResultService {
  private readonly http = inject(HttpClient);

  record(matchId: string, payload: RecordResultPayload): Observable<MatchResult> {
    return this.http.post<MatchResult>(`${environment.apiBaseUrl}/matches/${matchId}/result`, payload);
  }

  listByPool(poolId: string): Observable<MatchResult[]> {
    return this.http.get<MatchResult[]>(`${environment.apiBaseUrl}/pools/${poolId}/results`);
  }
}
