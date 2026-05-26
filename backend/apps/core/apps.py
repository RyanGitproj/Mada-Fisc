"""Configuration de l'application core."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration Django pour l'app core."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core — Utilitaires partagés"
