"""
Administration Django pour les modèles du module facturation.
"""
from django.contrib import admin

from .models import Client, Invoice


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Interface d'administration pour les clients."""

    list_display = ("company_name", "nif", "stat", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("company_name", "nif", "stat", "email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("company_name",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Interface d'administration pour les factures."""

    list_display = (
        "invoice_number", "client", "issue_date",
        "amount_ttc", "status",
    )
    list_filter = ("status", "issue_date")
    search_fields = ("invoice_number", "client__company_name")
    readonly_fields = ("tva_amount", "amount_ttc", "created_at", "updated_at")
    ordering = ("-issue_date",)
    date_hierarchy = "issue_date"
