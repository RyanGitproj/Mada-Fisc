"""
Exceptions métier centralisées pour mada_fisc_auto.
Toutes les exceptions métier héritent de MadaFiscBaseException.
"""
from typing import Any, Optional


class MadaFiscBaseException(Exception):
    """Exception de base pour toutes les erreurs métier."""

    def __init__(
        self,
        message: str,
        code: str = "error",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


# --- Exceptions Paie ---

class PayrollException(MadaFiscBaseException):
    """Exception de base pour le module paie."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, code="payroll_error", **kwargs)


class EmployeeNotFoundError(PayrollException):
    """L'employé demandé n'existe pas."""

    def __init__(self, employee_id: int) -> None:
        super().__init__(
            message=f"L'employé avec l'identifiant {employee_id} n'existe pas.",
            code="employee_not_found",
            details={"employee_id": employee_id},
        )


class DuplicatePayslipError(PayrollException):
    """Un bulletin de paie existe déjà pour cet employé et cette période."""

    def __init__(self, employee_id: int, month: int, year: int) -> None:
        super().__init__(
            message=(
                f"Un bulletin de paie existe déjà pour l'employé {employee_id} "
                f"pour la période {month:02d}/{year}."
            ),
            code="duplicate_payslip",
            details={"employee_id": employee_id, "month": month, "year": year},
        )


class InvalidPayrollPeriodError(PayrollException):
    """La période de paie est invalide."""

    def __init__(self, month: int, year: int) -> None:
        super().__init__(
            message=f"La période {month:02d}/{year} est invalide.",
            code="invalid_payroll_period",
            details={"month": month, "year": year},
        )


class PayrollCalculationError(PayrollException):
    """Erreur lors du calcul de la paie."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, code="payroll_calculation_error", **kwargs)


# --- Exceptions Facturation ---

class InvoicingException(MadaFiscBaseException):
    """Exception de base pour le module facturation."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, code="invoicing_error", **kwargs)


class ClientNotFoundError(InvoicingException):
    """Le client demandé n'existe pas."""

    def __init__(self, client_id: int) -> None:
        super().__init__(
            message=f"Le client avec l'identifiant {client_id} n'existe pas.",
            code="client_not_found",
            details={"client_id": client_id},
        )


class InvoiceNotFoundError(InvoicingException):
    """La facture demandée n'existe pas."""

    def __init__(self, invoice_id: int) -> None:
        super().__init__(
            message=f"La facture avec l'identifiant {invoice_id} n'existe pas.",
            code="invoice_not_found",
            details={"invoice_id": invoice_id},
        )


class InvalidInvoiceStatusTransition(InvoicingException):
    """Transition de statut de facture invalide."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            message=f"Transition de statut invalide : {current} → {target}.",
            code="invalid_status_transition",
            details={"current_status": current, "target_status": target},
        )


class DuplicateInvoiceNumberError(InvoicingException):
    """Numéro de facture en doublon."""

    def __init__(self, invoice_number: str) -> None:
        super().__init__(
            message=f"Le numéro de facture '{invoice_number}' existe déjà.",
            code="duplicate_invoice_number",
            details={"invoice_number": invoice_number},
        )


# --- Exceptions Configuration ---

class ConfigNotFoundError(MadaFiscBaseException):
    """Paramètre système introuvable."""

    def __init__(self, key: str) -> None:
        super().__init__(
            message=f"Le paramètre système '{key}' est introuvable.",
            code="config_not_found",
            details={"key": key},
        )
