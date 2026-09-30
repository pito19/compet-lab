import { DatePipe } from '@angular/common';
import { Component, DestroyRef, computed, effect, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../../../../core/services/auth.service';
import { MatchService } from '../../../../core/services/match.service';
import { Match, ScheduleConflict } from '../../../../core/models';
import { CompetitionContextService } from '../competition-context.service';
import { MatchStatusBadgeComponent } from '../match-status-badge/match-status-badge.component';
import { PoolPickerComponent } from '../pool-picker/pool-picker.component';

@Component({
  selector: 'cl-competition-calendar',
  imports: [ReactiveFormsModule, DatePipe, PoolPickerComponent, MatchStatusBadgeComponent],
  template: `
    <div class="calendar">
      @if (context.pools().length === 0) {
        <p class="card">Crée d'abord une poule dans l'onglet "Phases &amp; Poules".</p>
      } @else {
        <cl-pool-picker />

        @if (errorMessage(); as message) {
          <div class="error-banner">{{ message }}</div>
        }

        @if (isLoading()) {
          <p class="card">Chargement...</p>
        }

        @if (canManage()) {
          <form class="card calendar__generate" [formGroup]="form" (ngSubmit)="generate()">
            <label>
              Date de début
              <input type="datetime-local" formControlName="start_date" />
            </label>
            <label class="calendar__gap">
              Jours entre journées
              <input type="number" formControlName="days_between_matchdays" min="1" />
            </label>
            <button type="submit" class="primary" [disabled]="form.invalid || isGenerating()">
              {{ isGenerating() ? 'Génération...' : 'Générer le calendrier (round-robin)' }}
            </button>
          </form>
        }

        @if (conflicts().length > 0) {
          <div class="card">
            <h3>⚠ {{ conflicts().length }} conflit(s) détecté(s)</h3>
            @for (conflict of conflicts(); track conflict.match_id + conflict.type) {
              <div class="conflict-row">
                <span class="badge high">{{ conflict.severity }}</span>
                <span>{{ conflict.message }}</span>
              </div>
            }
          </div>
        }

        @if (matches().length === 0) {
          <p class="card">Aucun match généré pour cette poule.</p>
        } @else {
          <table class="card">
            <thead>
              <tr><th>Domicile</th><th>Extérieur</th><th>Date</th><th>Statut</th>@if (canManage()) {<th></th>}</tr>
            </thead>
            <tbody>
              @for (match of matches(); track match.id) {
                <tr>
                  <td>{{ teamName(match.home_team_id) }}</td>
                  <td>{{ teamName(match.away_team_id) }}</td>
                  <td>{{ match.scheduled_at ? (match.scheduled_at | date: 'short') : '—' }}</td>
                  <td><cl-match-status-badge [status]="match.status" /></td>
                  @if (canManage()) {
                    <td>
                      @if (match.status !== 'PLAYED') {
                        <input type="datetime-local" #newDate />
                        <button type="button" (click)="reschedule(match.id, newDate.value)">Reprogrammer</button>
                        @if (match.status !== 'POSTPONED') {
                          <button type="button" (click)="postpone(match.id)">Reporter</button>
                        }
                        @if (match.status !== 'CANCELLED') {
                          <button type="button" (click)="cancel(match.id)">Annuler</button>
                        }
                      }
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
      .calendar { display: flex; flex-direction: column; gap: 1rem; }
      .calendar__generate { display: flex; align-items: flex-end; gap: 0.8rem; }
      .calendar__gap { max-width: 160px; }
      .conflict-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.35rem 0; font-size: 0.85rem; }
      td input[type='datetime-local'] { margin-right: 0.4rem; }
    `,
  ],
})
export class CompetitionCalendarComponent {
  protected readonly context = inject(CompetitionContextService);
  private readonly destroyRef = inject(DestroyRef);
  protected readonly isLoading = signal(false);
  private readonly matchService = inject(MatchService);
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  protected readonly matches = signal<Match[]>([]);
  protected readonly conflicts = signal<ScheduleConflict[]>([]);
  protected readonly isGenerating = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    start_date: ['', Validators.required],
    days_between_matchdays: [7, [Validators.required, Validators.min(1)]],
  });

  private readonly teamNameById = computed(() => {
    const map = new Map<string, string>();
    for (const team of this.context.teams()) map.set(team.id, team.name);
    return map;
  });

  constructor() {
    // Reload matches/conflicts whenever the selected pool changes.
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


  protected generate(): void {
    const poolId = this.context.selectedPoolId();
    if (!poolId || this.form.invalid) return;

    if (this.matches().length > 0) {
      const confirmed = confirm(
        'Un calendrier existe déjà pour cette poule. Le régénérer supprimera tous les matchs ' +
          'non joués et les remplacera (les matchs déjà joués sont conservés). Continuer ?',
      );
      if (!confirmed) return;
    }

    this.isGenerating.set(true);
    this.errorMessage.set(null);

    const raw = this.form.getRawValue();
    this.matchService
      .generateSchedule(poolId, {
        start_date: new Date(raw.start_date).toISOString(),
        days_between_matchdays: raw.days_between_matchdays,
      })
      .subscribe({
        next: () => {
          this.isGenerating.set(false);
          this.loadPoolData(poolId);
        },
        error: (err: Error) => {
          this.isGenerating.set(false);
          this.errorMessage.set(err.message);
        },
      });
  }

  protected reschedule(matchId: string, newDateTimeLocal: string): void {
    if (!newDateTimeLocal) return;
    this.matchService.reschedule(matchId, { scheduled_at: new Date(newDateTimeLocal).toISOString() }).subscribe({
      next: () => {
        const poolId = this.context.selectedPoolId();
        if (poolId) this.loadPoolData(poolId);
      },
      error: (err: Error) => this.errorMessage.set(err.message),
    });
  }

  protected postpone(matchId: string): void {
    this.matchService.postpone(matchId).subscribe({
      next: () => {
        const poolId = this.context.selectedPoolId();
        if (poolId) this.loadPoolData(poolId);
      },
      error: (err: Error) => this.errorMessage.set(err.message),
    });
  }

  protected cancel(matchId: string): void {
    if (!confirm('Annuler ce match ? Cette action est réversible en le reprogrammant plus tard.')) return;
    this.matchService.cancel(matchId).subscribe({
      next: () => {
        const poolId = this.context.selectedPoolId();
        if (poolId) this.loadPoolData(poolId);
      },
      error: (err: Error) => this.errorMessage.set(err.message),
    });
  }

  private loadPoolData(poolId: string): void {
    this.isLoading.set(true);
    this.matchService
      .listByPool(poolId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (matches) => {
          this.matches.set(matches);
          this.isLoading.set(false);
        },
        error: (err: Error) => {
          this.errorMessage.set(err.message);
          this.isLoading.set(false);
        },
      });
    this.matchService
      .getConflicts(poolId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (conflicts) => this.conflicts.set(conflicts),
        error: (err: Error) => this.errorMessage.set(err.message),
      });
  }
}
