import { Component, inject, signal } from '@angular/core';
import { Observable } from 'rxjs';
import { Competition } from '../../../../core/models';
import { AuthService } from '../../../../core/services/auth.service';
import { CompetitionService } from '../../../../core/services/competition.service';
import { CompetitionContextService } from '../competition-context.service';

@Component({
  selector: 'cl-competition-overview',
  template: `
    @if (errorMessage(); as message) {
      <div class="error-banner">{{ message }}</div>
    }
    @if (context.competition(); as competition) {
      <div class="overview card">
        <dl>
          <dt>Catégorie</dt><dd>{{ competition.category || '—' }}</dd>
          <dt>Genre</dt><dd>{{ competition.gender }}</dd>
          <dt>Type</dt><dd>{{ competition.type }}</dd>
          <dt>Statut</dt><dd>{{ competition.status }}</dd>
          <dt>Publiée</dt><dd>{{ competition.is_published ? 'Oui' : 'Non' }}</dd>
          <dt>Équipes engagées</dt><dd>{{ context.teams().length }}</dd>
          <dt>Phases</dt><dd>{{ context.phases().length }}</dd>
          @if (competition.legacy_id) {
            <dt>Identifiant legacy</dt><dd>{{ competition.legacy_id }} <span class="badge medium">importée</span></dd>
          }
        </dl>

        @if (canManage()) {
          <div class="overview__actions">
            @if (competition.status === 'DRAFT') {
              <button class="primary" (click)="activate()">Activer</button>
            }
            @if (competition.status === 'ACTIVE' && !competition.is_published) {
              <button class="primary" (click)="publish()">Publier</button>
            }
            @if (competition.status !== 'CLOSED') {
              <button (click)="close()">Clôturer</button>
            }
          </div>
        }
      </div>
    }
  `,
  styles: [
    `
      dl { display: grid; grid-template-columns: max-content 1fr; gap: 0.4rem 1.2rem; margin: 0 0 1rem; }
      dt { color: var(--cl-color-text-muted); font-size: 0.8rem; }
      dd { margin: 0; }
      .overview__actions { display: flex; gap: 0.6rem; padding-top: 0.8rem; border-top: 1px solid var(--cl-color-border); }
    `,
  ],
})
export class CompetitionOverviewComponent {
  protected readonly context = inject(CompetitionContextService);
  private readonly competitionService = inject(CompetitionService);
  private readonly auth = inject(AuthService);

  protected canManage(): boolean {
    return this.auth.hasAnyRole('ADMIN', 'MANAGER');
  }

  protected readonly errorMessage = signal<string | null>(null);

  protected activate(): void {
    this.apply(this.competitionService.activate(this.context.competitionId()));
  }

  protected publish(): void {
    this.apply(this.competitionService.publish(this.context.competitionId()));
  }

  protected close(): void {
    this.apply(this.competitionService.close(this.context.competitionId()));
  }

  private apply(request: Observable<Competition>): void {
    this.errorMessage.set(null);
    request.subscribe({
      next: (competition) => this.context.competition.set(competition),
      error: (err: Error) => this.errorMessage.set(err.message),
    });
  }
}
