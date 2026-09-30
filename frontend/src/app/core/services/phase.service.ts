import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { CreatePhasePayload, CreatePoolPayload, Phase, Pool } from '../models';

@Injectable({ providedIn: 'root' })
export class PhaseService {
  private readonly http = inject(HttpClient);

  listPhases(competitionId: string): Observable<Phase[]> {
    return this.http.get<Phase[]>(`${environment.apiBaseUrl}/competitions/${competitionId}/phases`);
  }

  createPhase(competitionId: string, payload: CreatePhasePayload): Observable<Phase> {
    return this.http.post<Phase>(`${environment.apiBaseUrl}/competitions/${competitionId}/phases`, payload);
  }

  listPools(phaseId: string): Observable<Pool[]> {
    return this.http.get<Pool[]>(`${environment.apiBaseUrl}/phases/${phaseId}/pools`);
  }

  createPool(phaseId: string, payload: CreatePoolPayload): Observable<Pool> {
    return this.http.post<Pool>(`${environment.apiBaseUrl}/phases/${phaseId}/pools`, payload);
  }

  addTeamToPool(poolId: string, teamId: string): Observable<Pool> {
    return this.http.post<Pool>(`${environment.apiBaseUrl}/pools/${poolId}/teams`, { team_id: teamId });
  }
}
