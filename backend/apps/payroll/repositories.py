"""
Dépôts du module paie — abstraction d'accès aux données.
Toute requête DB passe par les repositories.
Les services appellent les repositories, jamais l'ORM directement.
"""
from decimal import Decimal
from typing import Optional

from django.db.models import QuerySet

from .models import Employee, Payslip


class EmployeeRepository:
    """Dépôt pour l'accès aux données des employés."""

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Récupérer un employé par son identifiant."""
        try:
            return Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return None

    def get_active_by_id(self, employee_id: int) -> Optional[Employee]:
        """Récupérer un employé actif par son identifiant."""
        try:
            return Employee.objects.get(pk=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return None

    def get_all_active(self) -> QuerySet[Employee]:
        """Récupérer tous les employés actifs."""
        return Employee.objects.filter(is_active=True).order_by("last_name", "first_name")

    def get_all(self) -> QuerySet[Employee]:
        """Récupérer tous les employés."""
        return Employee.objects.all().order_by("last_name", "first_name")

    def create(self, **kwargs: object) -> Employee:
        """Créer un nouvel employé."""
        return Employee.objects.create(**kwargs)  # type: ignore[arg-type]

    def update(self, employee: Employee, **kwargs: object) -> Employee:
        """Mettre à jour un employé."""
        for key, value in kwargs.items():
            setattr(employee, key, value)
        employee.save()
        return employee

    def soft_delete(self, employee: Employee) -> Employee:
        """Désactiver un employé (suppression logique)."""
        employee.is_active = False
        employee.save()
        return employee

    def count_active(self) -> int:
        """Compter les employés actifs."""
        return Employee.objects.filter(is_active=True).count()


class PayslipRepository:
    """Dépôt pour l'accès aux données des bulletins de paie."""

    def get_by_id(self, payslip_id: int) -> Optional[Payslip]:
        """Récupérer un bulletin par son identifiant."""
        try:
            return Payslip.objects.select_related("employee").get(pk=payslip_id)
        except Payslip.DoesNotExist:
            return None

    def get_by_employee_and_period(
        self, employee_id: int, month: int, year: int
    ) -> Optional[Payslip]:
        """Récupérer un bulletin pour un employé et une période donnés."""
        try:
            return Payslip.objects.get(employee_id=employee_id, month=month, year=year)
        except Payslip.DoesNotExist:
            return None

    def exists_for_period(self, employee_id: int, month: int, year: int) -> bool:
        """Vérifier si un bulletin existe déjà pour cette période."""
        return Payslip.objects.filter(
            employee_id=employee_id, month=month, year=year
        ).exists()

    def create(self, **kwargs: object) -> Payslip:
        """Créer un nouveau bulletin de paie."""
        return Payslip.objects.create(**kwargs)  # type: ignore[arg-type]

    def get_monthly_payslips(self, month: int, year: int) -> QuerySet[Payslip]:
        """Récupérer tous les bulletins d'un mois donné."""
        return Payslip.objects.select_related("employee").filter(
            month=month, year=year
        ).order_by("employee__last_name")

    def get_monthly_summary(self, month: int, year: int) -> dict:
        """Récupérer le résumé mensuel (totaux agrégés)."""
        from django.db.models import Sum, Count

        result = Payslip.objects.filter(month=month, year=year).aggregate(
            total_gross=Sum("gross_salary"),
            total_cnaps=Sum("cnaps_deduction"),
            total_ostie=Sum("ostie_deduction"),
            total_fmfp=Sum("fmfp_deduction"),
            total_irsa=Sum("irsa_tax"),
            total_net=Sum("net_salary"),
            count=Count("id"),
        )
        return {
            "total_gross": result["total_gross"] or Decimal("0"),
            "total_cnaps": result["total_cnaps"] or Decimal("0"),
            "total_ostie": result["total_ostie"] or Decimal("0"),
            "total_fmfp": result["total_fmfp"] or Decimal("0"),
            "total_irsa": result["total_irsa"] or Decimal("0"),
            "total_net": result["total_net"] or Decimal("0"),
            "count": result["count"] or 0,
        }

    def get_employee_payslips(self, employee_id: int) -> QuerySet[Payslip]:
        """Récupérer tous les bulletins d'un employé."""
        return Payslip.objects.filter(employee_id=employee_id).order_by("-year", "-month")

    def get_recent_payslips(self, limit: int = 5) -> QuerySet[Payslip]:
        """Récupérer les derniers bulletins générés."""
        return Payslip.objects.select_related("employee").order_by("-generated_at")[:limit]
