import { Component, DestroyRef, computed, effect, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../../../core/services/auth.service';
import { MatchService } from '../../../../core/services/match.service';
import { ResultService } from '../../../../core/services/result.service';
import { Match, MatchResult } from '../../../../core/models';
import { CompetitionContextService } from '../competition-context.service';
import { MatchStatusBadgeComponent } from '../match-status-badge/match-status-badge.component';
import { PoolPickerComponent } from '../pool-picker/pool-picker.component';

@Component({
  selector: 'cl-competition-results',
  imports: [PoolPickerComponent, MatchStatusBadgeComponent],
  template: `
    <div class="results">
      @if (context.pools().length === 0) {
        <p class="card">Crée d'abord une poule et génère un calendrier.</p>
      } @else {
        <cl-pool-picker />

        @if (errorMessage(); as message) {
          <div class="error-banner">{{ message }}</div>
        }

        @if (isLoading()) {
          <p class="card">Chargement...</p>
        }

        @if (matches().length === 0) {
          <p class="card">Aucun match pour cette poule. Génère d'abord un calendrier.</p>
        } @else {
          <table class="card">
            <thead>
              <tr><th>Domicile</th><th></th><th>Extérieur</th><th>Score</th><th>Statut</th>@if (canManage()) {<th></th>}</tr>
            </thead>
            <tbody>
              @for (match of matches(); track match.id) {
                <tr>
                  <td>{{ teamName(match.home_team_id) }}</td>
                  <td>vs</td>
                  <td>{{ teamName(match.away_team_id) }}</td>
                  <td class="num">
                    @if (resultFor(match.id); as result) {
                      {{ result.home_score }} – {{ result.away_score }}
                      @if (result.correction_count > 0) {
                        <span class="badge medium" title="Score corrigé après la première saisie">corrigé</span>
                      }
                    } @else {
                      —
                    }
                  </td>
                  <td><cl-match-status-badge [status]="match.status" /></td>
                  @if (canManage()) {
                    <td class="results__score-cell">
                      <input type="number" min="0" #homeScore style="width: 50px" [value]="resultFor(match.id)?.home_score ?? ''" />
                      -
                      <input type="number" min="0" #awayScore style="width: 50px" [value]="resultFor(match.id)?.away_score ?? ''" />
                      <button type="button" (click)="record(match.id, homeScore.value, awayScore.value)">
                        {{ match.status === 'PLAYED' ? 'Corriger' : 'Enregistrer' }}
                      </button>
                    </td>
                  }
                </tr>
              }
            </tbody>
          </table>
        }
      }
    </div>
  `,
  styles: [
    `
      .results { display: flex; flex-direction: column; gap: 1rem; }
      .results__score-cell { display: flex; align-items: center; gap: 0.4rem; }
    `,
  ],
})
export class CompetitionResultsComponent {
  protected readonly context = inject(CompetitionContextService);
  private readonly destroyRef = inject(DestroyRef);
  protected readonly isLoading = signal(false);
  private readonly matchService = inject(MatchService);
  private readonly resultService = inject(ResultService);
  private readonly auth = inject(AuthService);

  protected readonly matches = signal<Match[]>([]);
  protected readonly results = signal<MatchResult[]>([]);
  protected readonly errorMessage = signal<string | null>(null);

  private readonly teamNameById = computed(() => {
    const map = new Map<string, string>();
    for (const team of this.context.teams()) map.set(team.id, team.name);
    return map;
  });

  private readonly resultByMatchId = computed(() => {
    const map = new Map<string, MatchResult>();
    for (const result of this.results()) {
      if (result.match_id) map.set(result.match_id, result);
    }
    return map;
  });

  constructor() {
    effect(() => {
      const poolId = this.context.selectedPoolId();
      if (poolId) this.loadPoolData(poolId);
    });
  }

  protected canManage(): boolean {
    return this.auth.hasAnyRole('ADMIN', 'MANAGER');
  }

  protected teamName(teamId: string | null): string {
    if (!teamId) return '—';
    return this.teamNameById().get(teamId) ?? teamId;
  }

  protected resultFor(matchId: string): MatchResult | undefined {
    return this.resultByMatchId().get(matchId);
  }

  protected record(matchId: string, homeScoreRaw: string, awayScoreRaw: string): void {
    const home_score = Number(homeScoreRaw);
    const away_score = Number(awayScoreRaw);
    if (Number.isNaN(home_score) || Number.isNaN(away_score) || home_score < 0 || away_score < 0) {
      this.errorMessage.set('Merci de saisir deux scores valides (>= 0).');
      return;
    }

    this.errorMessage.set(null);
    this.resultService.record(matchId, { home_score, away_score }).subscribe({
      next: () => {
        const poolId = this.context.selectedPoolId();
        if (poolId) this.loadPoolData(poolId);
      },
      error: (err: Error) => this.errorMessage.set(err.message),
    });
  }

  private loadPoolData(poolId: string): void {
    this.isLoading.set(true);
    forkJoin({
      matches: this.matchService.listByPool(poolId),
      results: this.resultService.listByPool(poolId),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ matches, results }) => {
          this.matches.set(matches);
          this.results.set(results);
          this.isLoading.set(false);
        },
        error: (err: Error) => {
          this.errorMessage.set(err.message);
          this.isLoading.set(false);
        },
      });
  }
}
