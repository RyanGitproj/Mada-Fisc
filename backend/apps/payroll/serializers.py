"""
Serializers du module paie.
Séparés en InputSerializer (validation) et OutputSerializer (présentation).
"""
from decimal import Decimal

from rest_framework import serializers

from .models import Employee, Payslip


# --- Employee Serializers ---

class EmployeeInputSerializer(serializers.Serializer):
    """Serializer de validation pour la création/mise à jour d'un employé."""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, default="")
    base_salary = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0")
    )
    hire_date = serializers.DateField()
    birth_date = serializers.DateField(required=False, allow_null=True)
    dependants_count = serializers.IntegerField(min_value=0, default=0)
    cnaps_number = serializers.CharField(max_length=20, required=False, default="")
    organism_sanitaire = serializers.ChoiceField(
        choices=Employee.OrganismSanitaire.choices,
        default=Employee.OrganismSanitaire.OSTIE,
    )
    is_active = serializers.BooleanField(default=True)


class EmployeeOutputSerializer(serializers.ModelSerializer):
    """Serializer de présentation pour un employé."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = [
            "id", "first_name", "last_name", "full_name", "email", "phone",
            "base_salary", "hire_date", "birth_date", "dependants_count",
            "cnaps_number", "organism_sanitaire", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# --- Payslip Serializers ---

class PayslipGenerateInputSerializer(serializers.Serializer):
    """Serializer de validation pour la génération d'un bulletin."""
    employee_id = serializers.IntegerField(min_value=1)
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2000, max_value=2100)


class PayslipGenerateBatchInputSerializer(serializers.Serializer):
    """Serializer de validation pour la génération par lot."""
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2000, max_value=2100)


class PayslipOutputSerializer(serializers.ModelSerializer):
    """Serializer de présentation pour un bulletin de paie."""
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()

    class Meta:
        model = Payslip
        fields = [
            "id", "employee", "employee_name", "employee_email",
            "month", "year", "gross_salary",
            "cnaps_deduction", "ostie_deduction", "fmfp_deduction",
            "irsa_tax", "net_salary", "dependants_count",
            "is_paid", "paid_at", "generated_at",
        ]
        read_only_fields = [
            "id", "gross_salary", "cnaps_deduction", "ostie_deduction",
            "fmfp_deduction", "irsa_tax", "net_salary", "dependants_count",
            "is_paid", "paid_at", "generated_at",
        ]

    def get_employee_name(self, obj: Payslip) -> str:
        return obj.employee.full_name

    def get_employee_email(self, obj: Payslip) -> str:
        return obj.employee.email


class PayslipDetailOutputSerializer(PayslipOutputSerializer):
    """Serializer détaillé pour un bulletin de paie avec calculs IRSA."""

    class Meta(PayslipOutputSerializer.Meta):
        fields = PayslipOutputSerializer.Meta.fields + ["pdf_file"]


class MonthlySummaryOutputSerializer(serializers.Serializer):
    """Serializer pour le résumé mensuel de la paie."""
    total_gross = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_cnaps = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_ostie = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fmfp = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_irsa = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()
