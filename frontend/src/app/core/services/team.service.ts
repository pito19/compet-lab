import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { CreateTeamPayload, Team } from '../models';

@Injectable({ providedIn: 'root' })
export class TeamService {
  private readonly http = inject(HttpClient);

  list(competitionId: string): Observable<Team[]> {
    return this.http.get<Team[]>(`${environment.apiBaseUrl}/competitions/${competitionId}/teams`);
  }

  add(competitionId: string, payload: CreateTeamPayload): Observable<Team> {
    return this.http.post<Team>(`${environment.apiBaseUrl}/competitions/${competitionId}/teams`, payload);
  }
}
