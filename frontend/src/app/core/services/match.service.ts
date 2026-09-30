import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { GenerateSchedulePayload, Match, RescheduleMatchPayload, ScheduleConflict } from '../models';

@Injectable({ providedIn: 'root' })
export class MatchService {
  private readonly http = inject(HttpClient);

  generateSchedule(poolId: string, payload: GenerateSchedulePayload): Observable<Match[]> {
    return this.http.post<Match[]>(`${environment.apiBaseUrl}/pools/${poolId}/schedule`, payload);
  }

  listByPool(poolId: string): Observable<Match[]> {
    return this.http.get<Match[]>(`${environment.apiBaseUrl}/pools/${poolId}/matches`);
  }

  reschedule(matchId: string, payload: RescheduleMatchPayload): Observable<Match> {
    return this.http.patch<Match>(`${environment.apiBaseUrl}/matches/${matchId}`, payload);
  }

  postpone(matchId: string): Observable<Match> {
    return this.http.post<Match>(`${environment.apiBaseUrl}/matches/${matchId}/postpone`, {});
  }

  cancel(matchId: string): Observable<Match> {
    return this.http.post<Match>(`${environment.apiBaseUrl}/matches/${matchId}/cancel`, {});
  }

  getConflicts(poolId: string): Observable<ScheduleConflict[]> {
    return this.http.get<ScheduleConflict[]>(`${environment.apiBaseUrl}/pools/${poolId}/quality/conflicts`);
  }
}
