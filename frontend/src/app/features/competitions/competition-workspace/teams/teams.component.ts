import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../../../../core/services/auth.service';
import { TeamService } from '../../../../core/services/team.service';
import { CompetitionContextService } from '../competition-context.service';

@Component({
  selector: 'cl-competition-teams',
  imports: [ReactiveFormsModule],
  template: `
    <div class="teams">
      @if (canManage()) {
        <form class="card teams__form" [formGroup]="form" (ngSubmit)="submit()">
          <label>
            Nom de l'équipe
            <input formControlName="name" placeholder="AS Riverside" />
          </label>
          <label>
            Club
            <input formControlName="club_name" placeholder="AS Riverside" />
          </label>
          <button type="submit" class="primary" [disabled]="form.invalid || isSubmitting()">
            {{ isSubmitting() ? 'Ajout...' : '+ Ajouter' }}
          </button>
        </form>
      }

      @if (errorMessage(); as message) {
        <div class="error-banner">{{ message }}</div>
      }

      @if (context.teams().length === 0) {
        <p class="card">Aucune équipe engagée pour le moment.</p>
      } @else {
        <table class="card">
          <thead>
            <tr><th>Nom</th><th>Club</th><th>Affectée à une poule</th></tr>
          </thead>
          <tbody>
            @for (team of context.teams(); track team.id) {
              <tr>
                <td>{{ team.name }}</td>
                <td>{{ team.club_name }}</td>
                <td>{{ team.pool_id ? 'Oui' : 'Non' }}</td>
              </tr>
            }
          </tbody>
        </table>
      }
    </div>
  `,
  styles: [
    `
      .teams { display: flex; flex-direction: column; gap: 1rem; }
      .teams__form { display: flex; align-items: flex-end; gap: 0.8rem; }
      label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.8rem; flex: 1; }
    `,
  ],
})
export class CompetitionTeamsComponent {
  protected readonly context = inject(CompetitionContextService);
  private readonly teamService = inject(TeamService);
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  protected readonly isSubmitting = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(1)]],
    club_name: [''],
  });

  protected canManage(): boolean {
    return this.auth.hasAnyRole('ADMIN', 'MANAGER');
  }

  protected submit(): void {
    if (this.form.invalid) return;
    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.teamService.add(this.context.competitionId(), this.form.getRawValue()).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.form.reset();
        this.context.refreshTeams();
      },
      error: (err: Error) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(err.message);
      },
    });
  }
}
