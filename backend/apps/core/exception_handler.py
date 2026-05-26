"""
Gestionnaire d'exceptions centralisé pour DRF.
Transforme les exceptions métier en réponses API cohérentes.
"""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

from .exceptions import MadaFiscBaseException


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Gestionnaire d'exceptions DRF personnalisé.

    Gère :
    - Les exceptions métier MadaFiscBaseException → format API standardisé
    - Les exceptions DRF standard → délégation au handler par défaut
    """
    # D'abord, laisser DRF gérer ses propres exceptions
    response = drf_exception_handler(exc, context)

    if isinstance(exc, MadaFiscBaseException):
        # Mapper les codes d'erreur métier vers les codes HTTP
        http_status = _map_exception_to_http_status(exc)
        return Response(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=http_status,
        )

    if response is not None:
        # Enrichir les réponses d'erreur DRF standard
        error_data = response.data
        if isinstance(error_data, dict):
            response.data = {
                "error": {
                    "code": "validation_error",
                    "message": "Erreur de validation.",
                    "details": error_data,
                }
            }
        elif isinstance(error_data, list):
            response.data = {
                "error": {
                    "code": "validation_error",
                    "message": "Erreur de validation.",
                    "details": error_data,
                }
            }

    return response


def _map_exception_to_http_status(exc: MadaFiscBaseException) -> int:
    """Mapper les codes d'exception métier vers les codes HTTP."""
    from .exceptions import (
        EmployeeNotFoundError,
        ClientNotFoundError,
        InvoiceNotFoundError,
        DuplicatePayslipError,
        DuplicateInvoiceNumberError,
        InvalidPayrollPeriodError,
        InvalidInvoiceStatusTransition,
        ConfigNotFoundError,
    )

    not_found_codes = {
        EmployeeNotFoundError,
        ClientNotFoundError,
        InvoiceNotFoundError,
        ConfigNotFoundError,
    }
    conflict_codes = {
        DuplicatePayslipError,
        DuplicateInvoiceNumberError,
    }
    bad_request_codes = {
        InvalidPayrollPeriodError,
        InvalidInvoiceStatusTransition,
    }

    for exc_class in not_found_codes:
        if isinstance(exc, exc_class):
            return status.HTTP_404_NOT_FOUND

    for exc_class in conflict_codes:
        if isinstance(exc, exc_class):
            return status.HTTP_409_CONFLICT

    for exc_class in bad_request_codes:
        if isinstance(exc, exc_class):
            return status.HTTP_400_BAD_REQUEST

    return status.HTTP_500_INTERNAL_SERVER_ERROR
