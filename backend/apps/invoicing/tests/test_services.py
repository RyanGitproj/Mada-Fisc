"""
Tests unitaires du service de facturation.
"""
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from apps.invoicing.services import InvoiceCalculationService, InvoiceService
from apps.invoicing.models import Invoice
from apps.core.exceptions import InvalidInvoiceStatusTransition


class TestInvoiceCalculationService:
    """Tests du service de calcul de facturation."""

    def setup_method(self) -> None:
        self.service = InvoiceCalculationService(config_repo=MagicMock())

    def test_calcul_tva_20_pourcent(self) -> None:
        """Calcul TVA à 20% sur un montant HT."""
        result = self.service.calculate_tva(
            amount_ht=Decimal("100000"),
            tva_rate=Decimal("0.20"),
        )
        assert result["amount_ht"] == Decimal("100000")
        assert result["tva_amount"] == Decimal("20000.00")
        assert result["amount_ttc"] == Decimal("120000.00")

    def test_calcul_tva_montant_zero(self) -> None:
        """TVA sur un montant HT de zéro."""
        result = self.service.calculate_tva(
            amount_ht=Decimal("0"),
            tva_rate=Decimal("0.20"),
        )
        assert result["tva_amount"] == Decimal("0.00")
        assert result["amount_ttc"] == Decimal("0.00")

    def test_montant_negatif_rejete(self) -> None:
        """Un montant HT négatif doit lever une erreur."""
        with pytest.raises(ValueError):
            self.service.calculate_tva(
                amount_ht=Decimal("-1000"),
                tva_rate=Decimal("0.20"),
            )

    def test_grand_montant(self) -> None:
        """Calcul TVA sur un grand montant."""
        result = self.service.calculate_tva(
            amount_ht=Decimal("10000000"),
            tva_rate=Decimal("0.20"),
        )
        assert result["tva_amount"] == Decimal("2000000.00")
        assert result["amount_ttc"] == Decimal("12000000.00")


class TestInvoiceServiceStatusTransitions:
    """Tests des transitions de statut des factures."""

    def test_transitions_valides(self) -> None:
        """Les transitions valides doivent être autorisées."""
        assert Invoice.Status.SENT in InvoiceService.VALID_TRANSITIONS[Invoice.Status.DRAFT]
        assert Invoice.Status.PAID in InvoiceService.VALID_TRANSITIONS[Invoice.Status.SENT]
        assert Invoice.Status.OVERDUE in InvoiceService.VALID_TRANSITIONS[Invoice.Status.SENT]
        assert Invoice.Status.PAID in InvoiceService.VALID_TRANSITIONS[Invoice.Status.OVERDUE]

    def test_transitions_invalides(self) -> None:
        """Les transitions invalides doivent être rejetées."""
        # PAID → SENT : invalide
        assert Invoice.Status.SENT not in InvoiceService.VALID_TRANSITIONS[Invoice.Status.PAID]
        # PAID → DRAFT : invalide
        assert Invoice.Status.DRAFT not in InvoiceService.VALID_TRANSITIONS[Invoice.Status.PAID]
        # DRAFT → PAID : invalide (doit passer par SENT d'abord)
        assert Invoice.Status.PAID not in InvoiceService.VALID_TRANSITIONS[Invoice.Status.DRAFT]
        # DRAFT → OVERDUE : invalide
        assert Invoice.Status.OVERDUE not in InvoiceService.VALID_TRANSITIONS[Invoice.Status.DRAFT]

    def test_statut_paid_final(self) -> None:
        """Le statut PAID est final — aucune transition possible."""
        assert len(InvoiceService.VALID_TRANSITIONS[Invoice.Status.PAID]) == 0
