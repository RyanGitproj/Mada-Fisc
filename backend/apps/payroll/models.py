"""
Modèles du module paie — Employee et Payslip.
Les modèles ne contiennent aucune logique métier.
Toute la logique est dans services.py.
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Employee(models.Model):
    """
    Employé d'une PME malgache.
    Contient les informations nécessaires au calcul de la paie.
    """

    class OrganismSanitaire(models.TextChoices):
        OSTIE = "OSTIE", "OSTIE"
        AMIT = "AMIT", "AMIT"
        ESIA = "ESIA", "ESIA"
        FUNHECE = "FUNHECE", "FUNHECE"

    first_name = models.CharField(
        _("Prénom"),
        max_length=100,
    )
    last_name = models.CharField(
        _("Nom"),
        max_length=100,
    )
    email = models.EmailField(
        _("Adresse e-mail"),
        unique=True,
    )
    phone = models.CharField(
        _("Téléphone"),
        max_length=20,
        blank=True,
        default="",
    )
    base_salary = models.DecimalField(
        _("Salaire de base"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Salaire brut mensuel en Ariary"),
    )
    hire_date = models.DateField(
        _("Date d'embauche"),
    )
    birth_date = models.DateField(
        _("Date de naissance"),
        null=True,
        blank=True,
    )
    dependants_count = models.PositiveSmallIntegerField(
        _("Personnes à charge"),
        default=0,
        help_text=_("Nombre de personnes à charge pour la réduction IRSA"),
    )
    cnaps_number = models.CharField(
        _("Numéro CNaPS"),
        max_length=20,
        blank=True,
        default="",
    )
    organism_sanitaire = models.CharField(
        _("Organisme sanitaire"),
        max_length=10,
        choices=OrganismSanitaire.choices,
        default=OrganismSanitaire.OSTIE,
        help_text=_("OSTIE, AMIT, ESIA ou FUNHECE selon la région"),
    )
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("L'employé est-il toujours en activité ?"),
    )
    created_at = models.DateTimeField(
        _("Créé le"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Modifié le"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Employé")
        verbose_name_plural = _("Employés")
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"], name="idx_employee_name"),
            models.Index(fields=["is_active"], name="idx_employee_active"),
        ]

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self) -> str:
        """Nom complet de l'employé."""
        return f"{self.first_name} {self.last_name}"


class Payslip(models.Model):
    """
    Bulletin de paie mensuel.
    Chaque employé ne peut avoir qu'un seul bulletin par mois/année.
    Les montants sont des snapshots au moment du calcul.
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payslips",
        verbose_name=_("Employé"),
    )
    month = models.PositiveSmallIntegerField(
        _("Mois"),
        help_text=_("Mois du bulletin (1-12)"),
    )
    year = models.PositiveIntegerField(
        _("Année"),
        help_text=_("Année du bulletin"),
    )
    gross_salary = models.DecimalField(
        _("Salaire brut"),
        max_digits=12,
        decimal_places=2,
    )
    cnaps_deduction = models.DecimalField(
        _("Cotisation CNaPS salarié"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    ostie_deduction = models.DecimalField(
        _("Cotisation OSTIE/AMIT salarié"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    fmfp_deduction = models.DecimalField(
        _("Cotisation FMFP salarié"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    irsa_tax = models.DecimalField(
        _("IRSA"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    net_salary = models.DecimalField(
        _("Salaire net"),
        max_digits=12,
        decimal_places=2,
    )
    dependants_count = models.PositiveSmallIntegerField(
        _("Personnes à charge (snapshot)"),
        default=0,
        help_text=_("Nombre de personnes à charge au moment du calcul"),
    )
    is_paid = models.BooleanField(
        _("Payé"),
        default=False,
    )
    paid_at = models.DateTimeField(
        _("Date de paiement"),
        null=True,
        blank=True,
    )
    generated_at = models.DateTimeField(
        _("Date de génération"),
        auto_now_add=True,
    )
    pdf_file = models.FileField(
        _("Fichier PDF"),
        upload_to="payslips/%Y/%m/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Bulletin de paie")
        verbose_name_plural = _("Bulletins de paie")
        unique_together = ("employee", "month", "year")
        ordering = ["-year", "-month", "employee__last_name"]
        indexes = [
            models.Index(fields=["year", "month"], name="idx_payslip_period"),
            models.Index(fields=["is_paid"], name="idx_payslip_paid"),
        ]

    def __str__(self) -> str:
        return f"Bulletin {self.month:02d}/{self.year} — {self.employee}"
