"""Configuration de l'application payroll."""
from django.apps import AppConfig


class PayrollConfig(AppConfig):
    """Configuration Django pour l'app payroll."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payroll"
    verbose_name = "Paie — Employés & Bulletins"
