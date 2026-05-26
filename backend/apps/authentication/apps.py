"""Configuration de l'application authentication."""
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Configuration Django pour l'app authentication."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    verbose_name = "Authentification — JWT"
