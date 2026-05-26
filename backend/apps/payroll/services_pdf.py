"""
Service de génération PDF des bulletins de paie via WeasyPrint.
"""
import os
from pathlib import Path
from decimal import Decimal

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML

from apps.core.repositories import SystemConfigRepository
from apps.payroll.services import PayrollCalculationService


class PayslipPDFService:
    """Service de génération du PDF d'un bulletin de paie."""

    def __init__(self) -> None:
        self._config_repo = SystemConfigRepository()

    def generate(self, payslip: object) -> str:
        """
        Générer le PDF d'un bulletin de paie.

        Args:
            payslip: Instance du modèle Payslip

        Returns:
            Chemin du fichier PDF généré
        """
        # Récupérer les détails du calcul IRSA pour le contexte
        calc_service = PayrollCalculationService(config_repo=self._config_repo)
        result = calc_service.calculate(
            gross_salary=payslip.gross_salary,
            dependants=payslip.dependants_count,
        )

        # Calculer le total des déductions
        total_deductions = (
            payslip.cnaps_deduction
            + payslip.ostie_deduction
            + payslip.fmfp_deduction
        )

        # Contexte du template
        context = {
            "payslip": payslip,
            "employee": payslip.employee,
            "month": payslip.month,
            "year": payslip.year,
            "base_irsa": str(result.base_irsa),
            "bracket_details": result.bracket_details,
            "irsa_brut": str(result.irsa_brut),
            "irsa_reduction": str(result.irsa_reduction),
            "total_deductions": str(total_deductions),
            "company_name": os.environ.get("COMPANY_NAME", ""),
            "company_nif": os.environ.get("COMPANY_NIF", ""),
            "company_stat": os.environ.get("COMPANY_STAT", ""),
            "generated_date": payslip.generated_at.strftime("%d/%m/%Y %H:%M"),
        }

        # Rendre le template HTML
        html_string = render_to_string("pdf/payslip.html", context)

        # Générer le PDF
        pdf_dir = Path(settings.MEDIA_ROOT) / "payslips" / str(payslip.year) / f"{payslip.month:02d}"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"bulletin_{payslip.employee.last_name}_{payslip.month:02d}_{payslip.year}.pdf"
        pdf_path = pdf_dir / pdf_filename

        HTML(string=html_string).write_pdf(str(pdf_path))

        # Mettre à jour le champ pdf_file du bulletin
        payslip.pdf_file.name = f"payslips/{payslip.year}/{payslip.month:02d}/{pdf_filename}"
        payslip.save(update_fields=["pdf_file"])

        return str(pdf_path)
