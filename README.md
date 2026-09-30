# COMPET LAB — V1

Prototype d'architecture inspiré du domaine fonctionnel public de la gestion de compétitions sportives. **Ne prétend pas reproduire un système interne existant** — voir `COMPET-LAB-V1-SCOPE.md` pour le positionnement complet et les décisions de cadrage.

## Démarrage rapide

```bash
docker compose up --build
```

Au premier démarrage, le backend :
1. applique les migrations Alembic (`alembic upgrade head`) ;
2. exécute le seed (`python -m app.seed`) — crée 3 comptes de démo + un jeu de données minimal ;
3. démarre l'API sur `http://localhost:8000` (docs interactives sur `/docs`).

Le frontend Angular démarre sur `http://localhost:4200` (bootstrap à venir).

### Comptes de démonstration (créés par le seed)

| Email | Mot de passe | Rôle |
|---|---|---|
| admin@compet-lab.local | Admin123! | ADMIN |
| manager@compet-lab.local | Manager123! | MANAGER |
| viewer@compet-lab.local | Viewer123! | VIEWER |

## Architecture

```text
backend/
  app/
    domain/          # Entités + règles métier. Aucune dépendance framework.
    application/      # Use cases. Dépend uniquement des ports (Protocols) du domaine.
    infrastructure/    # SQLAlchemy, JWT, Legacy Adapter. Implémente les ports.
    api/               # FastAPI: routers, schémas Pydantic, DI, gestion d'erreurs.
    config/            # Settings (pydantic-settings, variables d'environnement).
  alembic/             # Migrations.
  tests/
    unit/              # Domaine + application, testés SANS base de données (fakes en mémoire).
    api/               # Tests bout en bout via TestClient (nécessitent l'environnement Docker).

frontend/              # Angular (bootstrap à venir)
```

### Principe de dépendance

```text
api  ──depends on──▶  application  ──depends on──▶  domain
                              ▲
infrastructure ───implements──┘   (via les Protocols définis dans domain/shared/ports.py)
```

Le domaine ne connaît ni FastAPI, ni SQLAlchemy, ni PostgreSQL. C'est ce qui permet de tester
`RankingService` (par exemple) avec de simples objets en mémoire — voir
`tests/unit/test_ranking_service.py`.

### Démonstration live du Legacy Adapter

`POST /api/legacy/import-competition` (ADMIN) accepte un enregistrement au format legacy
(`kind: "CHAMPIONNAT"`, `active_flag: "O"`, …) et le convertit en `Competition` moderne (avec `legacy_id`
conservé pour la traçabilité). À tester depuis `/docs` (Swagger).

### Le Legacy Adapter (Anti-Corruption Layer)

`infrastructure/legacy/` simule une source de données legacy (`LegacyCompetitionRecord`, encodages
et vocabulaire différents du domaine moderne) et l'`adapter.py` associé la convertit vers le domaine
moderne. C'est le seul endroit du code qui connaît le format legacy — la démonstration du principe
de découplage évoqué dans l'offre d'emploi source.

## Tests

```bash
cd backend
pip install -e ".[dev]"
pytest                        # tests unitaires (aucune base de données requise)
pytest tests/api               # tests API bout en bout (nécessite le backend + Postgres démarrés)
```

**Statut de vérification à ce stade** : la logique métier pure (round-robin, classement, règles de
transition d'état, unicité équipe/poule) a été exécutée et validée directement dans cet environnement
de génération, sans dépendance externe. Les tests nécessitant FastAPI/SQLAlchemy/PostgreSQL n'ont
**pas encore été exécutés dans un environnement réel** — à faire dès le premier `docker compose up`.

## Ce qui est fait / ce qui reste (V1)

Voir `COMPET-LAB-V1-SCOPE.md` pour le détail complet. En bref :

- [x] Domaine complet (Season, Competition, Phase, Pool, Team, Match, MatchResult, Standing, User, AuditEvent)
- [x] Use cases : Competition, Team, Phase/Pool, Scheduling (round-robin + conflits), Results, Rankings
- [x] Infrastructure : SQLAlchemy + repositories, JWT + RBAC, Legacy Adapter
- [x] API : Competitions, Teams, Phases/Pools, Matches, Results, Rankings, Audit, Auth, Public
- [x] Erreurs RFC 7807, pagination page/page_size
- [x] Migration Alembic initiale, Docker Compose, seed
- [x] 26 tests unitaires domaine + application, **exécutés et verts** (dont règles d'appartenance équipe/poule et services testés sans base via fakes)
- [ ] Tests API d'intégration exécutés en conditions réelles
- [x] CI minimal écrit (`.github/workflows/ci.yml` : ruff, pytest, build Angular, Gitleaks, Trivy) — **pas encore exécuté**
- [ ] 1 scénario Cypress critique
- [x] Frontend Angular 20 (standalone + Signals) : login, dashboard, workspace compétition (6 onglets : overview, teams, phases/pools, calendar, results, standings)

## Fonctionnalités ajoutées sur demande (29/09/2026)

Priorité choisie : résultats déjà saisis → confirmation avant régénération destructive →
annuler/reporter un match → hygiène. Tout est fait :

- **`GET /api/pools/{id}/results`** : liste les résultats déjà enregistrés pour une poule.
  L'onglet Résultats affiche maintenant les scores existants (visibles par tous les rôles) et
  pré-remplit les champs de saisie pour la correction.
- **Confirmation avant régénération** du calendrier si des matchs existent déjà pour la poule
  (`confirm()` natif, message explicite sur ce qui sera conservé/supprimé).
- **`POST /api/matches/{id}/postpone`** et **`/cancel`** : les règles existaient déjà dans le
  domaine (`Match.postpone()`, `Match.cancel()`), il ne manquait que l'exposition API. Les deux
  actions sont désormais auditées (`MATCH_POSTPONED`, `MATCH_CANCELLED`), et **`MATCH_RESCHEDULED`
  aussi** — un oubli découvert en cours de route : la reprogrammation d'un match ne créait encore
  aucun événement d'audit, alors que le doc de cadrage le prévoyait explicitement.
- **Hygiène** : `takeUntilDestroyed` sur les 3 composants qui font `effect()` + appel HTTP
  (Calendar, Results, Standings), états de chargement ajoutés sur les mêmes, composant partagé
  `MatchStatusBadge` (élimine la duplication Calendar/Results et distingue maintenant clairement
  les 4 statuts : `SCHEDULED`/`POSTPONED` en doré, `PLAYED` en vert, `CANCELLED` en rouge — avant,
  annulé et programmé avaient la même couleur).

## Sonar

Scaffolding ajouté : `sonar-project.properties` à la racine, job `sonar` dans
`.github/workflows/ci.yml` (récupère la couverture backend produite par le job `backend`).
**Guide pas à pas fourni séparément (`SONAR-GUIDE.md`)** : création du compte SonarCloud, du
projet, génération du token, secret GitHub, lecture des résultats. Nécessite un compte SonarCloud
et un token que je ne peux pas créer moi-même — à faire côté utilisateur, voir le guide.

## Bandeau "match en cours" (option A retenue)

Après discussion, l'option retenue est un **vrai statut `LIVE`** (machine à états explicite,
actions déclarées par un opérateur) plutôt qu'une heuristique basée sur l'horaire. **Pas encore
implémenté** — prochaine étape.

## Évolutions et optimisations (28/09/2026, sur retour de logs réels)

Le log du 29/09 confirme le cycle métier complet en conditions réelles : création, activation,
publication, clôture (avec 409 correctement renvoyé sur ajout d'équipe/phase après clôture),
calendrier, reprogrammation, conflits, résultat, classement. Aucune 500.

Deux points corrigés proactivement (faible risque, vrai gain) :

- **Index manquants sur les clés étrangères** (`alembic/versions/0002_fk_indexes.py`) : PostgreSQL
  n'indexe pas les FK automatiquement. Sans ça, `teams.competition_id`, `matches.pool_id`,
  `matches.home_team_id/away_team_id`, `pools.phase_id`, `phases.competition_id`,
  `audit_events.(entity_type, entity_id)` et `audit_events.occurred_at` dégradent en scan
  séquentiel à mesure que les tables grossissent. Index ajoutés.
- **Format d'erreur non homogène** : les 401/403 (levés via `HTTPException` dans les dépendances
  d'auth) renvoyaient le format par défaut de FastAPI (`{"detail": ...}`) alors que les erreurs
  métier (404/409/422) renvoyaient déjà du `application/problem+json`. Un handler unique
  (`api/error_handlers.py`) couvre maintenant toute `HTTPException`, y compris les 404 FastAPI sur
  route inconnue. Verrouillé par `tests/api/test_health.py` (nécessite FastAPI installé pour
  s'exécuter, non exécutable dans cet environnement de génération).

### Backlog restant, par ordre de valeur/effort (non fait, à prioriser ensemble)

| Amélioration | Effort | Valeur |
|---|---|---|
| Endpoint `GET /pools/{id}/results` (liste des résultats déjà saisis) — l'onglet Résultats n'affiche pas les scores existants | Faible | Élevée (UX) |
| Endpoints `POST /matches/{id}/postpone` et `/cancel` (les méthodes existent déjà dans le domaine, juste pas exposées) | Faible | Moyenne |
| Confirmation UI avant régénération destructive du calendrier | Faible | Moyenne (évite une perte de données accidentelle) |
| `takeUntilDestroyed` sur les `effect()` de Calendar/Results/Standings | Faible | Faible (bonne pratique, risque de fuite quasi nul ici) |
| États de chargement (spinners) sur les onglets autres que Dashboard | Faible | Faible (confort) |
| Extraire un composant `MatchStatusBadge` partagé (dupliqué dans Calendar/Results) | Faible | Faible (lisibilité) |

## Design et données (28/09/2026)

- **Identité visuelle** repensée : discrète, ancrée dans le métier (pupitre d'organisateur de
  compétition plutôt que site fan). Fond quasi noir à sous-teinte verte, texte craie, accent
  doré unique (feuille de match / tableau d'affichage), vert pelouse réservé à un seul usage :
  la zone de promotion sur le classement. Cartes à fine réglure au lieu d'ombres portées ; en-têtes
  de tableau en casse normale ; colonnes chiffrées en `tabular-nums`. Voir `styles.scss`.
- **Données de démonstration** : les 8 équipes seedées portent désormais de vrais noms de clubs
  français (PSG, OM, AS Monaco, OL, LOSC, Stade Rennais, RC Lens, OGC Nice), utilisés à des fins de
  réalisme uniquement — dataset entièrement fictif, aucune donnée réelle de joueur ou de club n'est
  impliquée (voir commentaire dans `app/seed.py`).

## Correctifs issus du premier `docker compose up --build` réel (28/09/2026)

Log réel fourni par l'utilisateur : la stack **démarre et fonctionne** (migration appliquée sans
erreur, seed exécuté, login OK, tous les onglets testés en lecture répondent 200, aucun 500,
CORS et JWT fonctionnels). Deux défauts repérés dans les logs et corrigés :

| Bug | Sévérité | Symptôme dans le log | Correctif |
|---|---|---|---|
| Healthcheck Postgres | Cosmétique (log noise) | `FATAL: database "compet" does not exist` toutes les 5s en boucle : `pg_isready -U compet` sans `-d` cible par défaut une base nommée comme l'utilisateur, qui n'existe pas (la vraie base est `compet_lab`) | `pg_isready -U compet -d compet_lab` dans `docker-compose.yml` |
| Secret JWT de dev trop court | Mineur (sécurité) | `InsecureKeyLengthWarning: The HMAC key is 20 bytes long, which is below the minimum recommended length of 32 bytes for SHA256` | Secret de dev par défaut allongé (`docker-compose.yml` et `config/settings.py`) |

Plus, sans lien avec un bug observé : `GET /` renvoyait 404 (visible dans le log) → redirige
maintenant vers `/docs`.

**Non couvert par ce premier run** (le testeur a seulement navigué en lecture) : génération de
calendrier, saisie de résultat, conflits, audit, legacy import, RBAC en écriture, cycle de vie
DRAFT/ACTIVE/CLOSED. À tester ensuite.

## Correctifs issus de la recette technique (28/09/2026)

Un agent QA autonome a fait tourner le projet de bout en bout (Postgres local, sans Docker,
Docker indisponible sur sa machine) et a produit un rapport complet. **4 bugs réels** ont été
trouvés, vérifiés un par un sur ce dépôt puis corrigés :

| Bug | Sévérité | Fichier | Correctif |
|---|---|---|---|
| Migration `users.email` déclarait l'unicité deux fois (colonne `unique=True` + index non-unique) → `alembic check` sale | Bloquant | `alembic/versions/0001_initial.py` | Un seul index, unique |
| `GET /pools/{id}/matches` et `.../quality/conflicts` sur poule inconnue → `200 []` au lieu de `404` | Mineur | `application/scheduling/use_cases.py` | Vérification d'existence + `NotFoundError` |
| `team_ids` de la réponse ne contenait pas l'équipe qu'on venait d'ajouter (le pool est rechargé depuis `teams.pool_id`, mais *avant* que ce champ soit persisté) | Mineur | `application/phases/use_cases.py` | Persister l'équipe avant de recharger la poule |
| `CreateCompetitionPayload.gender` obligatoire en TS alors qu'optionnel côté API → build de production impossible | Bloquant | `frontend/.../competition.model.ts` | `gender?: string` |

Chaque correctif est verrouillé par un test (`tests/unit/test_phase_service.py`,
`tests/unit/test_scheduling_service.py`). Suite complète relancée : **30/30 verts**.

Deux points de discussion soulevés par le rapport ont aussi été corrigés (peu coûteux, gain réel) :
- **Tri du classement sensible aux accents** (« Étoile du Nord » classait après « Union Bellevue »
  à égalité de points/différence de buts, à cause d'une comparaison brute par code point Unicode) →
  tri insensible aux accents/casse (`domain/rankings/entities.py`), sans nouvelle dépendance.
- **Liste des matchs sans `ORDER BY` explicite** (Postgres peut réordonner les lignes après un
  `UPDATE`) → `ORDER BY scheduled_at` ajouté.

Les autres points de discussion du rapport sont acceptés comme limitations documentées de la V1
(non corrigés, choix assumé) : deux formats d'erreur (401/403 natifs FastAPI vs RFC 7807 métier) à
homogénéiser en V1.1 ; seed non transactionnel au niveau entité ; régénération de calendrier
destructive sans confirmation UI ; `effect()`+`.subscribe()` sans `takeUntilDestroyed` dans
calendar/results/standings (bas risque : les requêtes HTTP se complètent d'elles-mêmes) ;
pagination partielle (seules `competitions`, `audit`, `public` sont paginées) ; `ng serve` sur un
hôte public nécessite `--allowed-hosts` (à documenter en déploiement, pas un bug applicatif).

## Frontend

```text
frontend/src/app/
  core/
    models/        # DTOs partagés, miroir des schémas Pydantic backend
    services/       # 1 service HttpClient par domaine (Competition, Team, Phase, Match, Result, Ranking, Season, Auth)
    interceptors/    # auth (Bearer JWT) + error (RFC 7807 -> message normalisé, déconnexion sur 401)
    guards/          # authGuard, roleGuard(...roles) -- fonctionnels, Angular 17+
  layout/shell/       # Header + navigation
  features/
    auth/login/
    dashboard/                          # liste + création de compétitions
    competitions/competition-workspace/  # conteneur à onglets + CompetitionContextService
                                          # (état partagé entre onglets via DI hiérarchique)
      overview/ teams/ phases/ calendar/ results/ standings/
```

Choix d'architecture à noter :
- **100% standalone**, aucun NgModule, routes en `loadComponent` (lazy loading par route).
- **Signals** pour tout l'état local et partagé (pas de NgRx pour une V1 de cette taille — sur-ingénierie évitée, comme pour le backend).
- `CompetitionContextService` est fourni au niveau du composant workspace (`providers: [...]`), pas `providedIn: 'root'` : une instance par visite de compétition, détruite automatiquement à la navigation.
- Le token JWT est stocké en `localStorage` pour ce prototype (voir commentaire dans `auth.service.ts` sur le compromis sécurité vs simplicité — en production, un cookie httpOnly via un BFF serait préférable).

**Non testé dans cet environnement de génération** (pas d'accès réseau pour `npm install`) : la compilation TypeScript et le rendu réel dans un navigateur. À vérifier au premier `docker compose up --build`.
