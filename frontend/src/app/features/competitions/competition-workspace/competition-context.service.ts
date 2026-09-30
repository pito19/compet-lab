import { Injectable, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { Competition, Phase, Pool, Team } from '../../../core/models';
import { CompetitionService } from '../../../core/services/competition.service';
import { PhaseService } from '../../../core/services/phase.service';
import { TeamService } from '../../../core/services/team.service';

export interface PoolWithPhase extends Pool {
  phase_name: string;
}

/**
 * Route-scoped state shared by every tab of the competition workspace.
 * Provided in CompetitionWorkspaceComponent's own `providers` array
 * (not `providedIn: 'root'`), so a fresh instance exists per workspace
 * visit and is automatically destroyed when navigating away.
 */
@Injectable()
export class CompetitionContextService {
  private readonly competitionService = inject(CompetitionService);
  private readonly teamService = inject(TeamService);
  private readonly phaseService = inject(PhaseService);

  readonly competitionId = signal<string>('');
  readonly competition = signal<Competition | null>(null);
  readonly teams = signal<Team[]>([]);
  readonly phases = signal<Phase[]>([]);
  readonly pools = signal<PoolWithPhase[]>([]);
  readonly selectedPoolId = signal<string | null>(null);
  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);

  init(competitionId: string): void {
    this.competitionId.set(competitionId);
    this.isLoading.set(true);
    this.loadError.set(null);
    // Reset state so navigating from one competition to another never
    // shows stale data from the previous one.
    this.competition.set(null);
    this.teams.set([]);
    this.phases.set([]);
    this.pools.set([]);
    this.selectedPoolId.set(null);

    forkJoin({
      competition: this.competitionService.get(competitionId),
      teams: this.teamService.list(competitionId),
      phases: this.phaseService.listPhases(competitionId),
    }).subscribe({
      next: ({ competition, teams, phases }) => {
        this.competition.set(competition);
        this.teams.set(teams);
        this.phases.set(phases);
        this.loadPools(phases);
      },
      error: (err: Error) => this.fail(err),
    });
  }

  refreshTeams(): void {
    this.teamService.list(this.competitionId()).subscribe({
      next: (teams) => this.teams.set(teams),
      error: (err: Error) => this.fail(err),
    });
  }

  refreshPhases(): void {
    this.phaseService.listPhases(this.competitionId()).subscribe({
      next: (phases) => {
        this.phases.set(phases);
        this.loadPools(phases);
      },
      error: (err: Error) => this.fail(err),
    });
  }

  refreshPools(): void {
    this.loadPools(this.phases());
  }

  private loadPools(phases: Phase[]): void {
    if (phases.length === 0) {
      this.pools.set([]);
      this.isLoading.set(false);
      return;
    }

    const requests = phases.map((phase) => this.phaseService.listPools(phase.id));

    forkJoin(requests).subscribe({
      next: (poolsByPhase) => {
        const flattened: PoolWithPhase[] = poolsByPhase.flatMap((pools, index) =>
          pools.map((pool) => ({ ...pool, phase_name: phases[index].name })),
        );
        this.pools.set(flattened);
        const stillValid = flattened.some((p) => p.id === this.selectedPoolId());
        if (!stillValid) {
          this.selectedPoolId.set(flattened[0]?.id ?? null);
        }
        this.isLoading.set(false);
      },
      error: (err: Error) => this.fail(err),
    });
  }

  private fail(err: Error): void {
    this.loadError.set(err.message);
    this.isLoading.set(false);
  }
}
