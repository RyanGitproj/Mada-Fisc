"""
Configuration Celery pour mada_fisc_auto.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("mada_fisc_auto")

# Charger la config depuis Django settings (préfixe CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Découverte automatique des tâches dans chaque app
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs: object) -> None:
    """Configurer les tâches périodiques via Celery Beat."""
    pass  # Les tâches sont gérées via django-celery-beat en base de données
