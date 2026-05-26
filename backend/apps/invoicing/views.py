"""
Vues DRF du module facturation.
Les views délèguent toute la logique aux services.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import (
    ClientNotFoundError,
    InvalidInvoiceStatusTransition,
    InvoiceNotFoundError,
)
from .models import Client, Invoice
from .repositories import ClientRepository, InvoiceRepository
from .serializers import (
    ClientInputSerializer,
    ClientOutputSerializer,
    InvoiceCreateInputSerializer,
    InvoiceStatusInputSerializer,
    InvoiceOutputSerializer,
    InvoiceDetailOutputSerializer,
)
from .services import InvoiceCalculationService, InvoiceService


class ClientViewSet(viewsets.ModelViewSet):
    """
    CRUD pour les clients (seulement list et create).

    list     : GET    /api/v1/invoicing/clients/
    create   : POST   /api/v1/invoicing/clients/
    retrieve : GET    /api/v1/invoicing/clients/{id}/
    """
    queryset = Client.objects.all()
    serializer_class = ClientOutputSerializer
    http_method_names = ['get', 'post']

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return ClientInputSerializer
        return ClientOutputSerializer

    def get_queryset(self):
        queryset = Client.objects.all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(company_name__icontains=search)
        return queryset.order_by("company_name")

    def perform_create(self, serializer: ClientInputSerializer) -> None:
        repo = ClientRepository()
        repo.create(**serializer.validated_data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    CRUD pour les factures.

    list     : GET    /api/v1/invoicing/invoices/
    create   : POST   /api/v1/invoicing/invoices/
    retrieve : GET    /api/v1/invoicing/invoices/{id}/
    status   : PATCH  /api/v1/invoicing/invoices/{id}/status/
    pdf      : GET    /api/v1/invoicing/invoices/{id}/pdf/
    """
    queryset = Invoice.objects.select_related("client").all()
    serializer_class = InvoiceOutputSerializer

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return InvoiceCreateInputSerializer
        if self.action == "retrieve":
            return InvoiceDetailOutputSerializer
        if self.action == "change_status":
            return InvoiceStatusInputSerializer
        return InvoiceOutputSerializer

    def get_queryset(self):
        queryset = Invoice.objects.select_related("client").all()
        status_filter = self.request.query_params.get("status")
        client_id = self.request.query_params.get("client_id")
        year = self.request.query_params.get("year")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if client_id:
            queryset = queryset.filter(client_id=int(client_id))
        if year:
            queryset = queryset.filter(issue_date__year=int(year))

        return queryset.order_by("-issue_date")

    def create(self, request: object, *args: object, **kwargs: object) -> Response:
        """Créer une nouvelle facture via le service."""
        input_serializer = InvoiceCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        invoice_repo = InvoiceRepository()
        client_repo = ClientRepository()
        calc_service = InvoiceCalculationService()
        invoice_service = InvoiceService(
            invoice_repo=invoice_repo,
            client_repo=client_repo,
            calc_service=calc_service,
        )

        try:
            invoice = invoice_service.create_invoice(
                client_id=input_serializer.validated_data["client_id"],
                amount_ht=input_serializer.validated_data["amount_ht"],
                due_date=input_serializer.validated_data["due_date"],
                issue_date=input_serializer.validated_data.get("issue_date"),
                notes=input_serializer.validated_data.get("notes", ""),
            )
        except ClientNotFoundError as e:
            return Response(
                {"error": {"code": e.code, "message": e.message}},
                status=status.HTTP_404_NOT_FOUND,
            )

        output_serializer = InvoiceOutputSerializer(invoice)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    def change_status(self, request: object, pk: int = None) -> Response:
        """Changer le statut d'une facture."""
        input_serializer = InvoiceStatusInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        invoice_repo = InvoiceRepository()
        client_repo = ClientRepository()
        calc_service = InvoiceCalculationService()
        invoice_service = InvoiceService(
            invoice_repo=invoice_repo,
            client_repo=client_repo,
            calc_service=calc_service,
        )

        try:
            invoice = invoice_service.change_status(
                invoice_id=pk,
                new_status=input_serializer.validated_data["status"],
            )
        except InvoiceNotFoundError as e:
            return Response(
                {"error": {"code": e.code, "message": e.message}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidInvoiceStatusTransition as e:
            return Response(
                {"error": {"code": e.code, "message": e.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = InvoiceOutputSerializer(invoice)
        return Response(output_serializer.data)

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request: object, pk: int = None) -> Response:
        """Télécharger le PDF de la facture."""
        invoice = self.get_object()
        if not invoice.pdf_file:
            return Response(
                {"error": {"code": "pdf_not_found", "message": "Le PDF n'a pas encore été généré."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        from django.http import FileResponse
        return FileResponse(
            invoice.pdf_file.open("rb"),
            content_type="application/pdf",
            filename=f"{invoice.invoice_number}.pdf",
        )
