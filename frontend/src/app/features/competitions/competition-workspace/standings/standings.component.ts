import { Component, DestroyRef, effect, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RankingService } from '../../../../core/services/ranking.service';
import { Standing } from '../../../../core/models';
import { CompetitionContextService } from '../competition-context.service';
import { PoolPickerComponent } from '../pool-picker/pool-picker.component';

@Component({
  imports: [PoolPickerComponent],
  selector: 'cl-competition-standings',
  template: `
    <div class="standings">
      @if (context.pools().length === 0) {
        <p class="card">Crée d'abord une poule.</p>
      } @else {
        <cl-pool-picker />

        @if (errorMessage(); as message) {
          <div class="error-banner">{{ message }}</div>
        }

        @if (isLoading()) {
          <p class="card">Chargement...</p>
        }

        @if (standings().length === 0) {
          <p class="card">Aucune équipe dans cette poule.</p>
        } @else {
          <table class="card">
            <thead>
              <tr>
                <th>#</th><th>Équipe</th><th>J</th><th>G</th><th>N</th><th>P</th>
                <th>BP</th><th>BC</th><th>Diff</th><th>Pts</th>
              </tr>
            </thead>
            <tbody>
              @for (standing of standings(); track standing.team_id; let i = $index) {
                <tr [class.promotion-zone]="i < 3">
                  <td>{{ i + 1 }}</td>
                  <td>{{ standing.team_name }}</td>
                  <td class="num">{{ standing.played }}</td>
                  <td class="num">{{ standing.wins }}</td>
                  <td class="num">{{ standing.draws }}</td>
                  <td class="num">{{ standing.losses }}</td>
                  <td class="num">{{ standing.goals_for }}</td>
                  <td class="num">{{ standing.goals_against }}</td>
                  <td class="num">{{ standing.goal_difference > 0 ? '+' : '' }}{{ standing.goal_difference }}</td>
                  <td class="num"><strong>{{ standing.points }}</strong></td>
                </tr>
              }
            </tbody>
          </table>
          <p class="standings__legend">Barre verte : zone de promotion (3 premières places).</p>
        }
      }
    </div>
  `,
  styles: [
    `
      .standings { display: flex; flex-direction: column; gap: 1rem; }
      .standings__legend { margin: -0.6rem 0 0; font-size: 0.78rem; color: var(--cl-color-text-muted); }
    `,
  ],
})
export class CompetitionStandingsComponent {
  protected readonly context = inject(CompetitionContextService);
  private readonly destroyRef = inject(DestroyRef);
  protected readonly isLoading = signal(false);
  private readonly rankingService = inject(RankingService);

  protected readonly standings = signal<Standing[]>([]);
  protected readonly errorMessage = signal<string | null>(null);

  constructor() {
    effect(() => {
      const poolId = this.context.selectedPoolId();
      if (poolId) this.loadStandings(poolId);
    });
  }


  private loadStandings(poolId: string): void {
    this.isLoading.set(true);
    this.rankingService
      .getStandings(poolId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (standings) => {
          this.standings.set(standings);
          this.isLoading.set(false);
        },
        error: (err: Error) => {
          this.errorMessage.set(err.message);
          this.isLoading.set(false);
        },
      });
  }
}
