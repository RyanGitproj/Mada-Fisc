"""
Dépôts du module facturation — abstraction d'accès aux données.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce

from .models import Client, Invoice


class ClientRepository:
    """Dépôt pour l'accès aux données des clients."""

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Récupérer un client par son identifiant."""
        try:
            return Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return None

    def get_active_by_id(self, client_id: int) -> Optional[Client]:
        """Récupérer un client actif par son identifiant."""
        try:
            return Client.objects.get(pk=client_id, is_active=True)
        except Client.DoesNotExist:
            return None

    def get_all_active(self):
        """Récupérer tous les clients actifs."""
        return Client.objects.filter(is_active=True).order_by("company_name")

    def get_all(self):
        """Récupérer tous les clients."""
        return Client.objects.all().order_by("company_name")

    def create(self, **kwargs) -> Client:
        """Créer un nouveau client."""
        return Client.objects.create(**kwargs)

    def update(self, client: Client, **kwargs) -> Client:
        """Mettre à jour un client."""
        for key, value in kwargs.items():
            setattr(client, key, value)
        client.save()
        return client

    def soft_delete(self, client: Client) -> Client:
        """Désactiver un client (suppression logique)."""
        client.is_active = False
        client.save()
        return client


class InvoiceRepository:
    """Dépôt pour l'accès aux données des factures."""

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Récupérer une facture par son identifiant."""
        try:
            return Invoice.objects.select_related("client").get(pk=invoice_id)
        except Invoice.DoesNotExist:
            return None

    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Récupérer une facture par son numéro."""
        try:
            return Invoice.objects.get(invoice_number=invoice_number)
        except Invoice.DoesNotExist:
            return None

    def create(self, **kwargs) -> Invoice:
        """Créer une nouvelle facture."""
        return Invoice.objects.create(**kwargs)

    def update_status(self, invoice: Invoice, status: str) -> Invoice:
        """Mettre à jour le statut d'une facture."""
        invoice.status = status
        invoice.save()
        return invoice

    def get_overdue_invoices(self) -> list[Invoice]:
        """Récupérer les factures en retard."""
        today = date.today()
        return list(
            Invoice.objects.filter(
                status=Invoice.Status.SENT,
                due_date__lt=today,
            )
        )

    def get_next_invoice_number(self, year: int) -> str:
        """
        Générer le prochain numéro de facture pour une année donnée.
        Format : INV-YYYY-NNNN
        """
        prefix = f"INV-{year}-"
        last_invoice = (
            Invoice.objects.filter(invoice_number__startswith=prefix)
            .order_by("-invoice_number")
            .first()
        )
        if last_invoice is None:
            return f"{prefix}0001"

        # Extraire le numéro séquentiel
        last_number = int(last_invoice.invoice_number.split("-")[-1])
        return f"{prefix}{last_number + 1:04d}"

    def get_client_invoices(self, client_id: int):
        """Récupérer toutes les factures d'un client."""
        return Invoice.objects.filter(client_id=client_id).order_by("-issue_date")

    def get_tva_collected(self, month: int, year: int) -> Decimal:
        """Calculer la TVA collectée pour un mois donné (factures payées)."""
        result = Invoice.objects.filter(
            status=Invoice.Status.PAID,
            issue_date__month=month,
            issue_date__year=year,
        ).aggregate(
            total_tva=Coalesce(Sum("tva_amount"), Decimal("0"))
        )
        return result["total_tva"]
