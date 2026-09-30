# COMPET LAB — V1 Scope (Baseline verrouillée)

**Statut :** Baseline de développement — remplace les zones ambiguës de `V1_Specification_&_Architecture_v1_0.md`
**Positionnement :** prototype inspiré du domaine public de gestion des compétitions sportives, destiné à démontrer une approche de modernisation d'un SI métier existant. Ne prétend pas reproduire le COMPET interne de la FFF.

---

## 1. Découpage V1 réelle / V1.1 discutable

### V1 réelle — codée, testée, démontrable de bout en bout

```text
Domaine
  Season, Competition, Phase, Pool, Team, Venue,
  Match, MatchResult, Standing, User, AuditEvent

Fonctionnel
  - CRUD Season / Competition
  - Équipes engagées + affectation en poule
  - Phases / Pools
  - Génération de calendrier (round-robin simple, aller unique)
  - Consultation / modification / report d'une rencontre
  - Saisie et validation d'un résultat -> recalcul classement
  - Classement = projection calculée, non éditable
  - Publication (endpoint public read-only séparé)
  - Détection de conflits de calendrier (sans moteur de recommandation)
  - Audit append-only sur les opérations sensibles
  - RBAC (ADMIN / MANAGER / VIEWER) via JWT

Architecture
  - Modular monolith, couches domain/application/infrastructure/api
  - Domain sans dépendance framework
  - Legacy Adapter fonctionnel sur l'entité Competition (Anti-Corruption Layer)
  - API publique séparée conceptuellement et techniquement de l'API de gestion

Frontend Angular
  - Dashboard
  - Competition workspace : Overview / Teams / Phases / Calendar / Results / Standings

Qualité
  - Tests unitaires domaine (règles métier)
  - Tests API (pytest + httpx)
  - Docker Compose (backend + frontend + PostgreSQL)
```

### V1.1 — conçue et défendable à l'oral, prototypée seulement si le temps le permet

```text
- Moteur de recommandation (suggestions de créneaux alternatifs)
- Data Quality panel complet (catalogue d'anomalies au-delà des conflits calendrier)
- AI Assistant (Explain / Investigate / Suggest)
- CI/CD complet avec Sonar, Gitleaks, Trivy
- E2E Cypress complet
```

**Règle :** rien de la colonne V1.1 n'entre dans la Definition of Done de la V1. On en parle, on montre le design, on ne le code pas au détriment du socle.

---

## 2. Décisions tranchées (précédemment implicites)

| Sujet | Décision |
|---|---|
| Génération de calendrier | Round-robin simple, un seul aller (pas d'aller-retour en V1). Régénération d'un calendrier existant = opération explicite qui supprime et recrée les matchs `SCHEDULED` non joués (jamais les matchs `PLAYED`). |
| Calcul du classement | Un seul règlement fixe : victoire = 3 pts, nul = 1 pt, défaite = 0 pt. Tri : points, puis différence de buts, puis buts marqués, puis ordre alphabétique. Pas de `RankingPolicy` paramétrable en V1 (sur-ingénierie évitée). |
| Authentification | JWT (OAuth2 Password Flow natif FastAPI). Comptes seedés en base (pas d'IdP externe). |
| Format d'erreur API | **`application/problem+json` (RFC 7807)** : `{"type", "title", "status", "detail", "instance"}`. |
| Idempotence schedule | `POST /schedule` échoue (409) si des matchs `PLAYED` existent déjà ; sinon régénère les matchs non joués. |
| Pagination | **`page` / `page_size`** sur tous les `GET` de collection, réponse enveloppée `{"items": [...], "total": n, "page": n, "page_size": n}`. |
| Audit — API | Ajout explicite : `GET /api/audit`, `GET /api/competitions/{id}/audit`. |
| CI/CD V1 | **Minimal mais réel dès la V1** (pas repoussé en V1.1) : lint, unit tests, tests API d'intégration, build, Gitleaks, Trivy, **1 seul scénario Cypress critique**. Sonar en V1.1 (quality gate). Implémenté après le vertical slice backend fonctionnel, pas avant. |
| Versions techniques | **FastAPI 0.141.1** confirmé (release officielle du 29/07/2026, vérifiée sur github.com/fastapi/fastapi/releases). **Angular 20 LTS** retenu par défaut plutôt qu'Angular 19 (EOL) — décision ouverte si une contrainte de compatibilité avec un environnement cible précis apparaît. |

---

## 3. Ce qui ne change pas par rapport à la spec précédente

- Domain model, relations, règles métier de base (§6-7 de la spec précédente)
- Architecture modular monolith + domain/application/infrastructure/api
- RBAC à 3 rôles
- Principe Legacy Adapter / Anti-Corruption Layer
- Posture entretien (« je ne prétends pas reproduire COMPET »)

---

## 4. Prochaine étape

Bootstrap technique : structure de repo backend (FastAPI) + frontend (Angular), avec un premier vertical slice fonctionnel sur Competition → Team → Phase/Pool → Match → Result → Standing, RBAC, Audit et Legacy Adapter.
