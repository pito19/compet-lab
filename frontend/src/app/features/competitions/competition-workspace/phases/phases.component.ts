import { Component, computed, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../../../../core/services/auth.service';
import { PhaseService } from '../../../../core/services/phase.service';
import { CompetitionContextService } from '../competition-context.service';

@Component({
  selector: 'cl-competition-phases',
  imports: [ReactiveFormsModule],
  template: `
    <div class="phases">
      @if (errorMessage(); as message) {
        <div class="error-banner">{{ message }}</div>
      }

      @if (canManage()) {
        <form class="card phases__form" [formGroup]="phaseForm" (ngSubmit)="createPhase()">
          <label>
            Nouvelle phase
            <input formControlName="name" placeholder="Phase Régulière" />
          </label>
          <label class="phases__order">
            Ordre
            <input type="number" formControlName="order" min="1" />
          </label>
          <button type="submit" class="primary" [disabled]="phaseForm.invalid || isCreatingPhase()">
            {{ isCreatingPhase() ? 'Création...' : '+ Phase' }}
          </button>
        </form>
      }

      @if (context.phases().length === 0) {
        <p class="card">Aucune phase créée pour le moment.</p>
      }

      @for (phase of context.phases(); track phase.id) {
        <div class="card phase-block">
          <div class="phase-block__header">
            <h3>{{ phase.name }}</h3>
            <span class="badge ok">ordre {{ phase.order }}</span>
          </div>

          @if (canManage()) {
            <form class="phases__form" [formGroup]="poolForm" (ngSubmit)="createPool(phase.id)">
              <label>
                Nouvelle poule
                <input formControlName="name" placeholder="Poule A" />
              </label>
              <button type="submit" class="primary" [disabled]="poolForm.invalid || isCreatingPool()">
                {{ isCreatingPool() ? 'Création...' : '+ Poule' }}
              </button>
            </form>
          }

          @for (pool of poolsFor(phase.id); track pool.id) {
            <div class="pool-block">
              <div class="pool-block__header">
                <strong>{{ pool.name }}</strong>
                <span class="badge medium">{{ pool.team_ids.length }} équipe(s)</span>
              </div>

              @if (canManage()) {
                <div class="pool-block__assign">
                  <select #teamSelect>
                    @for (team of unassignedTeams(); track team.id) {
                      <option [value]="team.id">{{ team.name }}</option>
                    }
                  </select>
                  <button
                    type="button"
                    [disabled]="unassignedTeams().length === 0 || isAssigning()"
                    (click)="assignTeam(pool.id, teamSelect.value)"
                  >
                    Affecter à cette poule
                  </button>
                </div>
              }
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .phases { display: flex; flex-direction: column; gap: 1rem; }
      .phases__form { display: flex; align-items: flex-end; gap: 0.7rem; margin-bottom: 0.9rem; }
      .phases__order { max-width: 90px; }
      label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.8rem; flex: 1; }
      .phase-block__header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.8rem; }
      .phase-block__header h3 { margin: 0; }
      .pool-block { border-top: 1px solid var(--cl-color-border); padding-top: 0.7rem; margin-top: 0.7rem; }
      .pool-block__header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; }
      .pool-block__assign { display: flex; gap: 0.5rem; }
    `,
  ],
})
export class CompetitionPhasesComponent {
  protected readonly context = inject(CompetitionContextService);
  private readonly phaseService = inject(PhaseService);
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  protected readonly isCreatingPhase = signal(false);
  protected readonly isCreatingPool = signal(false);
  protected readonly isAssigning = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly phaseForm = this.fb.nonNullable.group({
    name: ['', Validators.required],
    order: [1, [Validators.required, Validators.min(1)]],
  });

  protected readonly poolForm = this.fb.nonNullable.group({
    name: ['', Validators.required],
  });

  protected canManage(): boolean {
    return this.auth.hasAnyRole('ADMIN', 'MANAGER');
  }

  protected readonly unassignedTeams = computed(() => this.context.teams().filter((t) => !t.pool_id));

  protected poolsFor(phaseId: string) {
    return this.context.pools().filter((p) => p.phase_id === phaseId);
  }

  protected createPhase(): void {
    if (this.phaseForm.invalid) return;
    this.isCreatingPhase.set(true);
    this.errorMessage.set(null);

    this.phaseService.createPhase(this.context.competitionId(), this.phaseForm.getRawValue()).subscribe({
      next: () => {
        this.isCreatingPhase.set(false);
        this.phaseForm.reset({ order: 1 });
        this.context.refreshPhases();
      },
      error: (err: Error) => {
        this.isCreatingPhase.set(false);
        this.errorMessage.set(err.message);
      },
    });
  }

  protected createPool(phaseId: string): void {
    if (this.poolForm.invalid) return;
    this.isCreatingPool.set(true);
    this.errorMessage.set(null);

    this.phaseService.createPool(phaseId, this.poolForm.getRawValue()).subscribe({
      next: () => {
        this.isCreatingPool.set(false);
        this.poolForm.reset();
        this.context.refreshPools();
      },
      error: (err: Error) => {
        this.isCreatingPool.set(false);
        this.errorMessage.set(err.message);
      },
    });
  }

  protected assignTeam(poolId: string, teamId: string): void {
    if (!teamId) return;
    this.isAssigning.set(true);
    this.errorMessage.set(null);

    this.phaseService.addTeamToPool(poolId, teamId).subscribe({
      next: () => {
        this.isAssigning.set(false);
        this.context.refreshPools();
        this.context.refreshTeams();
      },
      error: (err: Error) => {
        this.isAssigning.set(false);
        this.errorMessage.set(err.message);
      },
    });
  }
}
