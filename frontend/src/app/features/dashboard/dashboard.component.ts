import { Component, OnInit, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { CompetitionService } from '../../core/services/competition.service';
import { SeasonService } from '../../core/services/season.service';
import { Competition, CompetitionType, Season } from '../../core/models';

@Component({
  selector: 'cl-dashboard',
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <div class="dashboard">
      <div class="dashboard__header">
        <h1>Compétitions</h1>
        @if (canManage()) {
          <button class="primary" (click)="showCreateForm.set(!showCreateForm())">
            {{ showCreateForm() ? 'Annuler' : '+ Nouvelle compétition' }}
          </button>
        }
      </div>

      @if (errorMessage(); as message) {
        <div class="error-banner">{{ message }}</div>
      }

      @if (showCreateForm()) {
        <form class="card" [formGroup]="form" (ngSubmit)="submit()">
          <div class="form-grid">
            <label>
              Saison
              <select formControlName="season_id">
                @for (season of seasons(); track season.id) {
                  <option [value]="season.id">{{ season.label }}</option>
                }
              </select>
            </label>
            <label>
              Nom
              <input formControlName="name" placeholder="U15 Régional 1" />
            </label>
            <label>
              Catégorie
              <input formControlName="category" placeholder="U15" />
            </label>
            <label>
              Type
              <select formControlName="type">
                <option value="CHAMPIONSHIP">Championnat</option>
                <option value="CUP">Coupe</option>
                <option value="TOURNAMENT">Tournoi</option>
              </select>
            </label>
          </div>
          <button type="submit" class="primary" [disabled]="form.invalid || isCreating()">
            {{ isCreating() ? 'Création...' : 'Créer' }}
          </button>
        </form>
      }

      @if (isLoading()) {
        <p>Chargement...</p>
      } @else if (competitions().length === 0) {
        <p class="card">Aucune compétition pour le moment.</p>
      } @else {
        <table class="card">
          <thead>
            <tr>
              <th>Nom</th>
              <th>Catégorie</th>
              <th>Statut</th>
              <th>Publiée</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            @for (competition of competitions(); track competition.id) {
              <tr>
                <td>{{ competition.name }}</td>
                <td>{{ competition.category }}</td>
                <td><span class="badge ok">{{ competition.status }}</span></td>
                <td>{{ competition.is_published ? 'Oui' : 'Non' }}</td>
                <td><a [routerLink]="['/competitions', competition.id]">Ouvrir →</a></td>
              </tr>
            }
          </tbody>
        </table>
      }
    </div>
  `,
  styles: [
    `
      .dashboard { display: flex; flex-direction: column; gap: 1.2rem; }
      .dashboard__header { display: flex; align-items: center; justify-content: space-between; }
      .form-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-bottom: 1rem; }
      label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.8rem; }
      a { color: var(--cl-color-accent); text-decoration: none; }
    `,
  ],
})
export class DashboardComponent implements OnInit {
  private readonly competitionService = inject(CompetitionService);
  private readonly seasonService = inject(SeasonService);
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  protected readonly competitions = signal<Competition[]>([]);
  protected readonly seasons = signal<Season[]>([]);
  protected readonly isLoading = signal(true);
  protected readonly isCreating = signal(false);
  protected readonly showCreateForm = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly canManage = () => this.auth.hasAnyRole('ADMIN', 'MANAGER');

  protected readonly form = this.fb.nonNullable.group({
    season_id: ['', Validators.required],
    name: ['', [Validators.required, Validators.minLength(2)]],
    category: [''],
    type: ['CHAMPIONSHIP' as CompetitionType, Validators.required],
  });

  ngOnInit(): void {
    this.loadCompetitions();
    if (this.canManage()) {
      this.seasonService.list().subscribe({
        next: (seasons) => {
          this.seasons.set(seasons);
          if (seasons.length > 0) {
            this.form.patchValue({ season_id: seasons[0].id });
          }
        },
        error: () => undefined, // non-blocking: creation form simply stays empty
      });
    }
  }

  private loadCompetitions(): void {
    this.isLoading.set(true);
    this.competitionService.list().subscribe({
      next: (page) => {
        this.competitions.set(page.items);
        this.isLoading.set(false);
      },
      error: (err: Error) => {
        this.errorMessage.set(err.message);
        this.isLoading.set(false);
      },
    });
  }

  protected submit(): void {
    if (this.form.invalid) return;
    this.isCreating.set(true);
    this.errorMessage.set(null);

    this.competitionService.create(this.form.getRawValue()).subscribe({
      next: () => {
        this.isCreating.set(false);
        this.showCreateForm.set(false);
        // keep the selected season so the form stays valid for the next creation
        this.form.reset({ season_id: this.form.getRawValue().season_id, type: 'CHAMPIONSHIP' });
        this.loadCompetitions();
      },
      error: (err: Error) => {
        this.isCreating.set(false);
        this.errorMessage.set(err.message);
      },
    });
  }
}
