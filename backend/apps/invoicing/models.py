"""
Modèles du module facturation — Client et Invoice.
Les modèles ne contiennent aucune logique métier.
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """
    Client d'une PME malgache.
    Contient les informations fiscales (NIF, STAT) nécessaires aux factures.
    """

    company_name = models.CharField(
        _("Raison sociale"),
        max_length=200,
    )
    nif = models.CharField(
        _("NIF"),
        max_length=30,
        blank=True,
        default="",
        help_text=_("Numéro d'Identification Fiscale"),
    )
    stat = models.CharField(
        _("STAT"),
        max_length=30,
        blank=True,
        default="",
        help_text=_("Statistique — numéro d'identification entreprise"),
    )
    email = models.EmailField(
        _("Adresse e-mail"),
        blank=True,
        default="",
    )
    phone = models.CharField(
        _("Téléphone"),
        max_length=20,
        blank=True,
        default="",
    )
    address = models.TextField(
        _("Adresse"),
        blank=True,
        default="",
    )
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
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
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ["company_name"]
        indexes = [
            models.Index(fields=["company_name"], name="idx_client_name"),
            models.Index(fields=["is_active"], name="idx_client_active"),
        ]

    def __str__(self) -> str:
        return self.company_name


class Invoice(models.Model):
    """
    Facture avec TVA à 20%.
    Le numéro est auto-généré au format INV-YYYY-NNNN.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Brouillon")
        SENT = "SENT", _("Envoyée")
        PAID = "PAID", _("Payée")
        OVERDUE = "OVERDUE", _("En retard")

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name=_("Client"),
    )
    invoice_number = models.CharField(
        _("Numéro de facture"),
        max_length=20,
        unique=True,
        help_text=_("Format : INV-YYYY-NNNN"),
    )
    issue_date = models.DateField(
        _("Date d'émission"),
        default=timezone.now,
    )
    due_date = models.DateField(
        _("Date d'échéance"),
    )
    amount_ht = models.DecimalField(
        _("Montant HT"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    tva_amount = models.DecimalField(
 _("Montant TVA"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    amount_ttc = models.DecimalField(
        _("Montant TTC"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    status = models.CharField(
        _("Statut"),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    notes = models.TextField(
        _("Notes"),
        blank=True,
        default="",
    )
    pdf_file = models.FileField(
        _("Fichier PDF"),
        upload_to="invoices/%Y/%m/",
        blank=True,
        null=True,
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
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ["-issue_date"]
        indexes = [
            models.Index(fields=["status"], name="idx_invoice_status"),
            models.Index(fields=["issue_date"], name="idx_invoice_date"),
            models.Index(fields=["due_date"], name="idx_invoice_due"),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_number} — {self.client.company_name}"

    @property
    def is_overdue(self) -> bool:
        """La facture est-elle en retard de paiement ?"""
        return self.status == self.Status.SENT and self.due_date < timezone.now().date()
