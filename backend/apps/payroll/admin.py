"""
Administration Django pour les modèles du module paie.
"""
from django.contrib import admin

from .models import Employee, Payslip


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Interface d'administration pour les employés."""

    list_display = (
        "last_name", "first_name", "email", "base_salary",
        "organism_sanitaire", "dependants_count", "is_active",
    )
    list_filter = ("is_active", "organism_sanitaire")
    search_fields = ("first_name", "last_name", "email", "cnaps_number")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("last_name", "first_name")

    fieldsets = (
        ("Identité", {
            "fields": ("first_name", "last_name", "email", "phone"),
        }),
        ("Emploi", {
            "fields": ("base_salary", "hire_date", "birth_date", "is_active"),
        }),
        ("Cotisations sociales", {
            "fields": ("cnaps_number", "organism_sanitaire", "dependants_count"),
        }),
        ("Métadonnées", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    """Interface d'administration pour les bulletins de paie."""

    list_display = (
        "employee", "month", "year", "gross_salary",
        "irsa_tax", "net_salary", "is_paid",
    )
    list_filter = ("year", "month", "is_paid")
    search_fields = ("employee__first_name", "employee__last_name")
    readonly_fields = ("generated_at",)
    ordering = ("-year", "-month")
    date_hierarchy = "generated_at"

    fieldsets = (
        ("Identification", {
            "fields": ("employee", "month", "year"),
        }),
        ("Montants", {
            "fields": (
                "gross_salary", "cnaps_deduction", "ostie_deduction",
                "fmfp_deduction", "irsa_tax", "net_salary",
            ),
        }),
        ("Détails", {
            "fields": ("dependants_count", "is_paid", "paid_at", "pdf_file"),
        }),
        ("Métadonnées", {
            "fields": ("generated_at",),
            "classes": ("collapse",),
        }),
    )
