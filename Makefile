.PHONY: help dev dev-build dev-up dev-down test migrate shell db-shell createsuperuser lint lint-backend lint-frontend format prod prod-up prod-down logs clean

# ============================================================
# mada_fisc_auto — Commandes de gestion du projet
# ============================================================

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Développement ---

dev-build: ## Construire les images Docker
	docker compose build

dev: ## Lancer l'environnement de développement
	docker compose up -d

dev-up: ## Lancer avec logs en temps réel
	docker compose up

dev-down: ## Arrêter l'environnement de développement
	docker compose down

# --- Base de données ---

migrate: ## Exécuter les migrations
	docker compose exec backend python manage.py migrate

makemigrations: ## Créer les migrations
	docker compose exec backend python manage.py makemigrations

createsuperuser: ## Créer un superutilisateur
	docker compose exec backend python manage.py createsuperuser

db-shell: ## Ouvrir le shell PostgreSQL
	docker compose exec db psql -U mada_user -d mada_fisc

shell: ## Ouvrir le shell Django
	docker compose exec backend python manage.py shell

# --- Tests ---

test: ## Lancer tous les tests
	docker compose exec backend pytest --tb=short -q

test-verbose: ## Lancer les tests en mode verbeux
	docker compose exec backend pytest -v

test-cov: ## Lancer les tests avec couverture
	docker compose exec backend pytest --cov=apps --cov-report=term-missing

test-payroll: ## Tests du module paie uniquement
	docker compose exec backend pytest apps/payroll/tests/ -v

test-invoicing: ## Tests du module facturation uniquement
	docker compose exec backend pytest apps/invoicing/tests/ -v

# --- Qualité du code ---

lint-backend: ## Linter le backend (ruff + mypy)
	docker compose exec backend ruff check apps/ config/
	docker compose exec backend mypy apps/ config/ --ignore-missing-imports

lint-frontend: ## Linter le frontend
	docker compose exec frontend npx ng lint

lint: lint-backend ## Linter tout le projet

format: ## Formater le code backend
	docker compose exec backend black apps/ config/
	docker compose exec backend ruff check --fix apps/ config/

# --- Production ---

prod-build: ## Construire les images de production
	docker compose -f docker-compose.prod.yml build

prod-up: ## Lancer en production
	docker compose -f docker-compose.prod.yml up -d

prod-down: ## Arrêter la production
	docker compose -f docker-compose.prod.yml down

# --- Utilitaires ---

logs: ## Afficher les logs
	docker compose logs -f

logs-backend: ## Logs du backend uniquement
	docker compose logs -f backend

clean: ## Nettoyer les volumes et images
	docker compose down -v --rmi local

collectstatic: ## Collecter les fichiers statiques
	docker compose exec backend python manage.py collectstatic --noinput

loaddata: ## Charger les données initiales (SystemConfig)
	docker compose exec backend python manage.py loaddata system_config
