import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Competition, CreateCompetitionPayload, Page } from '../models';

@Injectable({ providedIn: 'root' })
export class CompetitionService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/competitions`;

  list(page = 1, pageSize = 20): Observable<Page<Competition>> {
    return this.http.get<Page<Competition>>(this.baseUrl, {
      params: { page, page_size: pageSize },
    });
  }

  get(id: string): Observable<Competition> {
    return this.http.get<Competition>(`${this.baseUrl}/${id}`);
  }

  create(payload: CreateCompetitionPayload): Observable<Competition> {
    return this.http.post<Competition>(this.baseUrl, payload);
  }

  rename(id: string, name: string): Observable<Competition> {
    return this.http.patch<Competition>(`${this.baseUrl}/${id}`, { name });
  }

  activate(id: string): Observable<Competition> {
    return this.http.post<Competition>(`${this.baseUrl}/${id}/activate`, {});
  }

  close(id: string): Observable<Competition> {
    return this.http.post<Competition>(`${this.baseUrl}/${id}/close`, {});
  }

  publish(id: string): Observable<Competition> {
    return this.http.post<Competition>(`${this.baseUrl}/${id}/publish`, {});
  }
}
