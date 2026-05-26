"""
Administration Django pour le modèle SystemConfig.
"""
from django.contrib import admin

from .models import SystemConfig


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """Interface d'administration pour les paramètres système."""

    list_display = ("key", "value", "description", "updated_at")
    search_fields = ("key", "description")
    readonly_fields = ("updated_at",)
    ordering = ("key",)

    fieldsets = (
        ("Paramètre", {
            "fields": ("key", "value", "description"),
        }),
        ("Métadonnées", {
            "fields": ("updated_at",),
            "classes": ("collapse",),
        }),
    )
