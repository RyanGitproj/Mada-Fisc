"""
Service de génération PDF des factures via WeasyPrint.
"""
import os
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML


class InvoicePDFService:
    """Service de génération du PDF d'une facture."""

    def generate(self, invoice: object) -> str:
        """
        Générer le PDF d'une facture.

        Args:
            invoice: Instance du modèle Invoice

        Returns:
            Chemin du fichier PDF généré
        """
        context = {
            "invoice": invoice,
            "company_name": os.environ.get("COMPANY_NAME", ""),
            "company_nif": os.environ.get("COMPANY_NIF", ""),
            "company_stat": os.environ.get("COMPANY_STAT", ""),
            "company_address": os.environ.get("COMPANY_ADDRESS", ""),
            "generated_date": invoice.created_at.strftime("%d/%m/%Y %H:%M"),
        }

        # Rendre le template HTML
        html_string = render_to_string("pdf/invoice.html", context)

        # Générer le PDF
        pdf_dir = Path(settings.MEDIA_ROOT) / "invoices" / str(invoice.issue_date.year) / f"{invoice.issue_date.month:02d}"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"{invoice.invoice_number}.pdf"
        pdf_path = pdf_dir / pdf_filename

        HTML(string=html_string).write_pdf(str(pdf_path))

        # Mettre à jour le champ pdf_file de la facture
        invoice.pdf_file.name = f"invoices/{invoice.issue_date.year}/{invoice.issue_date.month:02d}/{pdf_filename}"
        invoice.save(update_fields=["pdf_file"])

        return str(pdf_path)
