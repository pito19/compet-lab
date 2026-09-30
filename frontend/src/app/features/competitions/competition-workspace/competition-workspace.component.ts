import { Component, DestroyRef, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { CompetitionContextService } from './competition-context.service';

@Component({
  selector: 'cl-competition-workspace',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  providers: [CompetitionContextService],
  template: `
    @if (context.competition(); as competition) {
      <div class="workspace">
        <div class="workspace__header">
          <h1>{{ competition.name }}</h1>
          <span class="badge ok">{{ competition.status }}</span>
        </div>

        <nav class="workspace__tabs">
          <a routerLink="overview" routerLinkActive="active">Vue d'ensemble</a>
          <a routerLink="teams" routerLinkActive="active">Équipes</a>
          <a routerLink="phases" routerLinkActive="active">Phases &amp; Poules</a>
          <a routerLink="calendar" routerLinkActive="active">Calendrier</a>
          <a routerLink="results" routerLinkActive="active">Résultats</a>
          <a routerLink="standings" routerLinkActive="active">Classement</a>
        </nav>

        <div class="workspace__content">
          <router-outlet />
        </div>
      </div>
    } @else if (context.loadError(); as error) {
      <div class="error-banner">{{ error }}</div>
    } @else {
      <p>Chargement de la compétition...</p>
    }
  `,
  styles: [
    `
      .workspace__header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; }
      .workspace__tabs {
        display: flex; gap: 0.4rem; border-bottom: 1px solid var(--cl-color-border);
        margin-bottom: 1.2rem; flex-wrap: wrap;
      }
      .workspace__tabs a {
        padding: 0.55rem 0.9rem; color: var(--cl-color-text-muted); text-decoration: none;
        font-size: 0.85rem; border-bottom: 2px solid transparent;
      }
      .workspace__tabs a.active { color: var(--cl-color-accent); border-bottom-color: var(--cl-color-accent); }
    `,
  ],
})
export class CompetitionWorkspaceComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  protected readonly context = inject(CompetitionContextService);

  private readonly destroyRef = inject(DestroyRef);

  ngOnInit(): void {
    // Subscribing (rather than reading the snapshot) keeps the workspace
    // correct if the route param changes while the component is reused.
    this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((params) => {
      const competitionId = params.get('competitionId');
      if (competitionId) {
        this.context.init(competitionId);
      }
    });
  }
}
