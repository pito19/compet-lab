import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: '',
    loadComponent: () => import('./layout/shell/shell.component').then((m) => m.ShellComponent),
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },
      {
        path: 'competitions/:competitionId',
        loadComponent: () =>
          import('./features/competitions/competition-workspace/competition-workspace.component').then(
            (m) => m.CompetitionWorkspaceComponent,
          ),
        children: [
          { path: '', pathMatch: 'full', redirectTo: 'overview' },
          {
            path: 'overview',
            loadComponent: () =>
              import('./features/competitions/competition-workspace/overview/overview.component').then(
                (m) => m.CompetitionOverviewComponent,
              ),
          },
          {
            path: 'teams',
            loadComponent: () =>
              import('./features/competitions/competition-workspace/teams/teams.component').then(
                (m) => m.CompetitionTeamsComponent,
              ),
          },
          {
            path: 'phases',
            loadComponent: () =>
              import('./features/competitions/competition-workspace/phases/phases.component').then(
                (m) => m.CompetitionPhasesComponent,
              ),
          },
          {
            path: 'calendar',
            loadComponent: () =>
              import('./features/competitions/competition-workspace/calendar/calendar.component').then(
                (m) => m.CompetitionCalendarComponent,
              ),
          },
          {
            path: 'results',
            loadComponent: () =>
              import('./features/competitions/competition-workspace/results/results.component').then(
                (m) => m.CompetitionResultsComponent,
              ),
          },
          {
            path: 'standings',
            loadComponent: () =>
              import('./features/competitions/competition-workspace/standings/standings.component').then(
                (m) => m.CompetitionStandingsComponent,
              ),
          },
        ],
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
