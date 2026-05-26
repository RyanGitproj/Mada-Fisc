"""
Vues du tableau de bord — métriques agrégées.
"""
from decimal import Decimal
from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payroll.models import Employee, Payslip
from apps.invoicing.models import Invoice


class DashboardSummaryView(APIView):
    """
    Vue agrégée du tableau de bord.
    Retourne les métriques clés pour le mois en cours.
    """

    def get(self, request: object) -> Response:
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        # Masse salariale du mois
        payroll_summary = Payslip.objects.filter(
            month=current_month,
            year=current_year,
        ).aggregate(
            total_gross=Coalesce(Sum("gross_salary"), Decimal("0")),
            total_net=Coalesce(Sum("net_salary"), Decimal("0")),
            total_irsa=Coalesce(Sum("irsa_tax"), Decimal("0")),
            count=Count("id"),
        )

        # Employés actifs
        active_employees = Employee.objects.filter(is_active=True).count()

        # TVA collectée ce mois (factures payées)
        tva_collected = Invoice.objects.filter(
            status=Invoice.Status.PAID,
            issue_date__month=current_month,
            issue_date__year=current_year,
        ).aggregate(
            total_tva=Coalesce(Sum("tva_amount"), Decimal("0")),
        )["total_tva"]

        # Factures en attente
        pending_invoices = Invoice.objects.filter(
            status__in=[Invoice.Status.DRAFT, Invoice.Status.SENT],
        ).aggregate(
            count=Count("id"),
            total_ht=Coalesce(Sum("amount_ht"), Decimal("0")),
        )

        # Factures en retard
        overdue_invoices = Invoice.objects.filter(
            status=Invoice.Status.OVERDUE,
        ).aggregate(
            count=Count("id"),
            total_ht=Coalesce(Sum("amount_ht"), Decimal("0")),
        )

        # Derniers bulletins générés
        recent_payslips = Payslip.objects.select_related("employee").order_by(
            "-generated_at"
        )[:5]
        recent_payslips_data = [
            {
                "id": ps.id,
                "employee_name": f"{ps.employee.first_name} {ps.employee.last_name}",
                "month": ps.month,
                "year": ps.year,
                "net_salary": str(ps.net_salary),
                "generated_at": ps.generated_at.isoformat(),
            }
            for ps in recent_payslips
        ]

        data = {
            "periode": {"mois": current_month, "annee": current_year},
            "payroll": {
                "masse_salariale_brute": str(payroll_summary["total_gross"]),
                "masse_salariale_nette": str(payroll_summary["total_net"]),
                "total_irsa": str(payroll_summary["total_irsa"]),
                "nombre_bulletins": payroll_summary["count"],
                "employes_actifs": active_employees,
            },
            "invoicing": {
                "tva_collectee": str(tva_collected),
                "factures_en_attente": {
                    "nombre": pending_invoices["count"],
                    "montant_ht": str(pending_invoices["total_ht"]),
                },
                "factures_en_retard": {
                    "nombre": overdue_invoices["count"],
                    "montant_ht": str(overdue_invoices["total_ht"]),
                },
            },
            "derniers_bulletins": recent_payslips_data,
        }

        return Response(data)
