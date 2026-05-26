"""Configuration de l'application invoicing."""
from django.apps import AppConfig


class InvoicingConfig(AppConfig):
    """Configuration Django pour l'app invoicing."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.invoicing"
    verbose_name = "Facturation — Clients & Factures"
