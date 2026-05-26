"""
Vues DRF du module paie.
Les views délèguent toute la logique aux services.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.exceptions import EmployeeNotFoundError, DuplicatePayslipError
from .models import Employee, Payslip
from .repositories import EmployeeRepository, PayslipRepository
from .serializers import (
    EmployeeInputSerializer,
    EmployeeOutputSerializer,
    PayslipGenerateInputSerializer,
    PayslipGenerateBatchInputSerializer,
    PayslipOutputSerializer,
    PayslipDetailOutputSerializer,
    MonthlySummaryOutputSerializer,
)
from .services import PayrollCalculationService, PayslipService


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD pour les employés.

    list     : GET    /api/v1/payroll/employees/
    create   : POST   /api/v1/payroll/employees/
    retrieve : GET    /api/v1/payroll/employees/{id}/
    update   : PUT    /api/v1/payroll/employees/{id}/
    partial  : PATCH  /api/v1/payroll/employees/{id}/
    delete   : DELETE /api/v1/payroll/employees/{id}/
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeOutputSerializer

    def get_serializer_class(self) -> type:
        if self.action in ("create", "update", "partial_update"):
            return EmployeeInputSerializer
        return EmployeeOutputSerializer

    def get_queryset(self):
        queryset = Employee.objects.all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        return queryset.order_by("last_name", "first_name")

    def perform_create(self, serializer: EmployeeInputSerializer) -> None:
        repo = EmployeeRepository()
        validated_data = serializer.validated_data
        repo.create(**validated_data)

    def perform_update(self, serializer: EmployeeInputSerializer) -> None:
        repo = EmployeeRepository()
        validated_data = serializer.validated_data
        repo.update(self.get_object(), **validated_data)

    def perform_destroy(self, instance: Employee) -> None:
        repo = EmployeeRepository()
        repo.soft_delete(instance)


class PayslipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Consultation et génération des bulletins de paie.

    list     : GET    /api/v1/payroll/payslips/
    retrieve : GET    /api/v1/payroll/payslips/{id}/
    generate : POST   /api/v1/payroll/payslips/generate/
    batch    : POST   /api/v1/payroll/payslips/generate-batch/
    summary  : GET    /api/v1/payroll/payslips/monthly-summary/
    pdf      : GET    /api/v1/payroll/payslips/{id}/pdf/
    """
    queryset = Payslip.objects.select_related("employee").all()
    serializer_class = PayslipOutputSerializer

    def get_queryset(self):
        queryset = Payslip.objects.select_related("employee").all()
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        employee_id = self.request.query_params.get("employee_id")

        if month:
            queryset = queryset.filter(month=int(month))
        if year:
            queryset = queryset.filter(year=int(year))
        if employee_id:
            queryset = queryset.filter(employee_id=int(employee_id))

        return queryset.order_by("-year", "-month", "employee__last_name")

    def get_serializer_class(self) -> type:
        if self.action == "retrieve":
            return PayslipDetailOutputSerializer
        return PayslipOutputSerializer

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request: object) -> Response:
        """Générer un bulletin de paie pour un employé et une période."""
        input_serializer = PayslipGenerateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        payslip_repo = PayslipRepository()
        employee_repo = EmployeeRepository()
        calc_service = PayrollCalculationService()
        payslip_service = PayslipService(
            payslip_repo=payslip_repo,
            employee_repo=employee_repo,
            calc_service=calc_service,
        )

        try:
            result = payslip_service.generate_payslip(
                employee_id=input_serializer.validated_data["employee_id"],
                month=input_serializer.validated_data["month"],
                year=input_serializer.validated_data["year"],
            )
        except EmployeeNotFoundError as e:
            return Response(
                {"error": {"code": e.code, "message": e.message}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except DuplicatePayslipError as e:
            return Response(
                {"error": {"code": e.code, "message": e.message}},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": "Bulletin de paie généré avec succès.",
                "data": {
                    "gross_salary": str(result.gross_salary),
                    "cnaps_deduction": str(result.cnaps_deduction),
                    "ostie_deduction": str(result.ostie_deduction),
                    "fmfp_deduction": str(result.fmfp_deduction),
                    "base_irsa": str(result.base_irsa),
                    "irsa_tax": str(result.irsa_final),
                    "net_salary": str(result.net_salary),
                    "dependants_count": result.dependants_count,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="generate-batch")
    def generate_batch(self, request: object) -> Response:
        """Générer les bulletins de paie pour tous les employés actifs."""
        input_serializer = PayslipGenerateBatchInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        payslip_repo = PayslipRepository()
        employee_repo = EmployeeRepository()
        calc_service = PayrollCalculationService()
        payslip_service = PayslipService(
            payslip_repo=payslip_repo,
            employee_repo=employee_repo,
            calc_service=calc_service,
        )

        results = payslip_service.generate_batch_payslips(
            month=input_serializer.validated_data["month"],
            year=input_serializer.validated_data["year"],
        )

        return Response(
            {
                "message": f"{len(results)} bulletin(s) de paie généré(s).",
                "count": len(results),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="monthly-summary")
    def monthly_summary(self, request: object) -> Response:
        """Résumé mensuel agrégé de la paie."""
        month = int(request.query_params.get("month", 0))
        year = int(request.query_params.get("year", 0))

        if not (1 <= month <= 12 and year >= 2000):
            return Response(
                {"error": {"code": "invalid_period", "message": "Mois et année requis (?month=6&year=2026)"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        repo = PayslipRepository()
        summary = repo.get_monthly_summary(month, year)
        output_serializer = MonthlySummaryOutputSerializer(summary)
        return Response(output_serializer.data)

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request: object, pk: int = None) -> Response:
        """Télécharger le PDF du bulletin de paie."""
        payslip = self.get_object()
        if not payslip.pdf_file:
            return Response(
                {"error": {"code": "pdf_not_found", "message": "Le PDF n'a pas encore été généré."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        from django.http import FileResponse
        return FileResponse(
            payslip.pdf_file.open("rb"),
            content_type="application/pdf",
            filename=f"bulletin_{payslip.employee.last_name}_{payslip.month:02d}_{payslip.year}.pdf",
        )
