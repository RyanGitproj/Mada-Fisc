"""
Services du module facturation — logique métier pure.

InvoiceCalculationService : calcul TVA, génération numéro facture.
InvoiceService : orchestration de la création et gestion des factures.
"""
from datetime import date, timedelta
from decimal import Decimal

from apps.core.exceptions import (
    ClientNotFoundError,
    DuplicateInvoiceNumberError,
    InvalidInvoiceStatusTransition,
    InvoiceNotFoundError,
)
from apps.core.repositories import SystemConfigRepository
from .models import Invoice
from .repositories import ClientRepository, InvoiceRepository


class InvoiceCalculationService:
    """
    Service de calcul pour la facturation.
    Pur, sans dépendance Django ni HTTP.
    """

    def __init__(
        self,
        config_repo: SystemConfigRepository | None = None,
    ) -> None:
        self._config_repo = config_repo or SystemConfigRepository()

    def calculate_tva(self, amount_ht: Decimal, tva_rate: Decimal | None = None) -> dict:
        """
        Calculer la TVA et le montant TTC.

        Args:
            amount_ht: Montant hors taxes
            tva_rate: Taux de TVA (défaut: 20% depuis SystemConfig)

        Returns:
            Dictionnaire avec amount_ht, tva_amount, amount_ttc, tva_rate
        """
        if amount_ht < 0:
            raise ValueError("Le montant HT ne peut pas être négatif.")

        if tva_rate is None:
            tva_rate = self._config_repo.get_value("TVA_RATE")

        tva_amount = (amount_ht * tva_rate).quantize(Decimal("0.01"))
        amount_ttc = amount_ht + tva_amount

        return {
            "amount_ht": amount_ht,
            "tva_rate": tva_rate,
            "tva_amount": tva_amount,
            "amount_ttc": amount_ttc,
        }


class InvoiceService:
    """
    Service d'orchestration de la gestion des factures.

    Coordonne le calcul TVA, la persistance et les changements de statut.
    """

    # Transitions de statut autorisées
    VALID_TRANSITIONS: dict[str, set[str]] = {
        Invoice.Status.DRAFT: {Invoice.Status.SENT},
        Invoice.Status.SENT: {Invoice.Status.PAID, Invoice.Status.OVERDUE},
        Invoice.Status.OVERDUE: {Invoice.Status.PAID},
        Invoice.Status.PAID: set(),  # Aucune transition depuis PAID
    }

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        client_repo: ClientRepository,
        calc_service: InvoiceCalculationService,
    ) -> None:
        self._invoice_repo = invoice_repo
        self._client_repo = client_repo
        self._calc_service = calc_service

    def create_invoice(
        self,
        client_id: int,
        amount_ht: Decimal,
        due_date: date,
        issue_date: date | None = None,
        notes: str = "",
    ) -> Invoice:
        """
        Créer une nouvelle facture.

        Args:
            client_id: Identifiant du client
            amount_ht: Montant hors taxes
            due_date: Date d'échéance
            issue_date: Date d'émission (défaut: aujourd'hui)
            notes: Notes facultatives

        Returns:
            La facture créée

        Raises:
            ClientNotFoundError: Si le client n'existe pas
        """
        # Vérifier que le client existe
        client = self._client_repo.get_active_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(client_id)

        # Calcul TVA
        calc_result = self._calc_service.calculate_tva(amount_ht)

        # Générer le numéro de facture
        year = issue_date.year if issue_date else date.today().year
        invoice_number = self._invoice_repo.get_next_invoice_number(year)

        # Créer la facture
        invoice = self._invoice_repo.create(
            client_id=client_id,
            invoice_number=invoice_number,
            issue_date=issue_date or date.today(),
            due_date=due_date,
            amount_ht=calc_result["amount_ht"],
            tva_amount=calc_result["tva_amount"],
            amount_ttc=calc_result["amount_ttc"],
            notes=notes,
            status=Invoice.Status.DRAFT,
        )

        return invoice

    def change_status(self, invoice_id: int, new_status: str) -> Invoice:
        """
        Changer le statut d'une facture.

        Args:
            invoice_id: Identifiant de la facture
            new_status: Nouveau statut

        Returns:
            La facture mise à jour

        Raises:
            InvoiceNotFoundError: Si la facture n'existe pas
            InvalidInvoiceStatusTransition: Si la transition est invalide
        """
        invoice = self._invoice_repo.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(invoice_id)

        current_status = invoice.status
        if new_status not in self.VALID_TRANSITIONS.get(current_status, set()):
            raise InvalidInvoiceStatusTransition(current_status, new_status)

        return self._invoice_repo.update_status(invoice, new_status)

    def mark_overdue_invoices(self) -> int:
        """
        Marquer les factures envoyées dont la date d'échéance est dépassée.

        Returns:
            Nombre de factures marquées en retard
        """
        overdue_invoices = self._invoice_repo.get_overdue_invoices()
        count = 0
        for invoice in overdue_invoices:
            self._invoice_repo.update_status(invoice, Invoice.Status.OVERDUE)
            count += 1
        return count
