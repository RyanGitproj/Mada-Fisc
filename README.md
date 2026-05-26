# MadaFisc Auto — Paie, IRSA & Facturation pour PME Madagascar

Application professionnelle de gestion de la paie, du calcul IRSA et de la facturation TVA pour les PME malgaches. Conforme à la Loi de Finances n° 2025-021 et au décret de mars 2026.

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| API Backend | Django REST Framework | Django 5.x / DRF 3.15 |
| Frontend SPA | Angular | 18 (standalone components) |
| Base de données | PostgreSQL | 16 |
| Cache & Broker | Redis | 7 |
| Tâches asynchrones | Celery + django-celery-beat | 5.x |
| Génération PDF | WeasyPrint | 62+ |
| Conteneurisation | Docker Compose | 3.9 |

## Architecture

```
mada_fisc_auto/
├── backend/                  # Django REST API
│   ├── config/               # settings, urls, wsgi, asgi, celery
│   │   └── settings/
│   │       ├── base.py       # settings communs
│   │       ├── development.py # DEBUG=True, eager Celery
│   │       └── production.py # HTTPS, Sentry, ManifestStatic
│   ├── apps/
│   │   ├── core/             # SystemConfig, exceptions, permissions, dashboard
│   │   ├── authentication/   # JWT login/refresh/logout
│   │   ├── payroll/          # employés, bulletins, calcul IRSA
│   │   └── invoicing/        # clients, factures, TVA
│   ├── templates/pdf/        # templates WeasyPrint (bulletin, facture)
│   └── requirements/         # base.txt, dev.txt, prod.txt
├── frontend/                 # Angular 18 SPA
│   └── src/app/
│       ├── core/             # auth, guards, interceptors, error-handler
│       ├── features/         # dashboard, payroll, invoicing (lazy-loaded)
│       └── shared/           # sidebar, breadcrumb, currencyMga pipe
└── docker-compose.yml
```

### Principes de qualité

- **Pas de logique métier dans les views/serializers** : tout passe par le service layer
- **Pas de requêtes DB dans les services** : tout passe par les repositories
- **Typage strict** : Python type hints + mypy / TypeScript strict mode
- **Aucune valeur métier en dur** : table SystemConfig en base de données
- **Tests unitaires obligatoires** : pytest pour le calcul IRSA
- **Gestion des erreurs centralisée** : DRF custom exception handler + Angular global error handler

## Données légales Madagascar 2026

### Cotisations sociales (depuis le 1er mars 2026)

| Cotisation | Part salarié | Part employeur | Base de calcul |
|------------|-------------|----------------|----------------|
| CNaPS | 1% | 13% | MIN(brut, 2 400 000 Ar) |
| OSTIE/AMIT | 1% | 5% | MIN(brut, 2 400 000 Ar) |
| FMFP | 1% | 1% | MIN(brut, 2 400 000 Ar) |

- SME = 300 000 Ar/mois
- Plafond = 8 × SME = 2 400 000 Ar

### Barème IRSA 2026

| Tranche | Fourchette (Ar/mois) | Taux |
|---------|----------------------|------|
| 1 | ≤ 350 000 | 0% |
| 2 | 350 001 – 400 000 | 5% |
| 3 | 400 001 – 500 000 | 10% |
| 4 | 500 001 – 600 000 | 15% |
| 5 | 600 001 – 4 000 000 | 20% |
| 6 | > 4 000 000 | 25% |

- Minimum de perception : 3 000 Ar (LF 2026)
- Réduction : 2 000 Ar par personne à charge
- Arrondi de la base imposable : centaine inférieure

### TVA

- Taux : 20%
- amount_ttc = amount_ht × 1.20

## Installation — Développement

### Prérequis

- Docker Desktop (ou Docker Engine + Docker Compose)
- Make (optionnel, pour les commandes du Makefile)

### Étapes

```bash
# 1. Cloner le dépôt
git clone <repo-url> && cd mada_fisc_auto

# 2. Copier le fichier d'environnement
cp .env.example .env

# 3. Construire et lancer les conteneurs
make dev-build
make dev

# 4. Exécuter les migrations
make migrate

# 5. Créer un superutilisateur
make createsuperuser

# 6. Accéder à l'application
# Backend API  : http://localhost:8000/api/v1/
# Admin Django : http://localhost:8000/admin/
# Frontend SPA : http://localhost:4200/
```

### Commandes utiles

```bash
make test              # Lancer tous les tests
make test-payroll      # Tests du module paie
make test-cov          # Tests avec couverture
make lint-backend      # Linter le backend (ruff + mypy)
make shell             # Shell Django
make db-shell          # Shell PostgreSQL
make logs              # Voir les logs
make dev-down          # Arrêter les conteneurs
```

## Installation — Production

```bash
# 1. Configurer les variables d'environnement de production
cp .env.example .env
# Éditer .env : SECRET_KEY, POSTGRES_PASSWORD, EMAIL_*, etc.

# 2. Construire et lancer
make prod-build
make prod-up

# 3. Migrations + données initiales
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 4. Collecter les fichiers statiques
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## API REST — Endpoints

Tous les endpoints sont préfixés par `/api/v1/` et protégés par JWT (sauf auth).

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/login/` | Obtenir access + refresh tokens |
| POST | `/auth/refresh/` | Rafraîchir le token d'accès |
| POST | `/auth/logout/` | Blacklister le refresh token |

### Paie

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/payroll/employees/` | Liste des employés |
| POST | `/payroll/employees/` | Créer un employé |
| GET | `/payroll/employees/{id}/` | Détail d'un employé |
| PUT | `/payroll/employees/{id}/` | Mettre à jour un employé |
| DELETE | `/payroll/employees/{id}/` | Désactiver un employé |
| GET | `/payroll/payslips/` | Liste des bulletins |
| POST | `/payroll/payslips/generate/` | Générer un bulletin |
| POST | `/payroll/payslips/generate-batch/` | Générer pour tous les actifs |
| GET | `/payroll/payslips/monthly-summary/` | Résumé mensuel |
| GET | `/payroll/payslips/{id}/pdf/` | Télécharger le PDF |

### Facturation

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/invoicing/clients/` | Liste des clients |
| POST | `/invoicing/clients/` | Créer un client |
| GET | `/invoicing/invoices/` | Liste des factures |
| POST | `/invoicing/invoices/` | Créer une facture |
| PATCH | `/invoicing/invoices/{id}/status/` | Changer le statut |
| GET | `/invoicing/invoices/{id}/pdf/` | Télécharger le PDF |

### Dashboard

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/dashboard/summary/` | Métriques agrégées du mois |

## Tests

### Tests unitaires du calcul IRSA

Les tests valident le calcul IRSA selon le barème 2026 officiel :

| Cas | Brut | CNaPS | OSTIE | FMFP | Base IRSA | IRSA | Net |
|-----|------|-------|-------|------|-----------|------|-----|
| Exonéré | 350 000 | 3 500 | 3 500 | 3 500 | 339 500 | 0 | 339 500 |
| Multi-tranches | 500 000 | 5 000 | 5 000 | 5 000 | 485 000 | 11 000 | 474 000 |
| Haut salaire | 1 500 000 | 15 000 | 15 000 | 15 000 | 1 455 000 | 198 500 | 1 256 500 |
| 2 personnes à charge | 500 000 | 5 000 | 5 000 | 5 000 | 485 000 | 7 000 | 478 000 |
| Plafond cotisations | 3 000 000 | 24 000 | 24 000 | 24 000 | 2 928 000 | — | — |
| Minimum perception | 361 000 | 3 610 | 3 610 | 3 610 | 350 100 | 3 000 | — |

```bash
# Lancer les tests IRSA
make test-payroll
```

## Tâches planifiées (Celery Beat)

Timezone : Indian/Antananarivo (UTC+3)

| Tâche | Planification | Description |
|-------|---------------|-------------|
| `mark_overdue_invoices` | 1er du mois à 08:00 | Marquer les factures en retard |
| `send_overdue_reminders` | 1er du mois à 09:00 | Envoyer les rappels par e-mail |

## Licence

Projet privé — tous droits réservés.
