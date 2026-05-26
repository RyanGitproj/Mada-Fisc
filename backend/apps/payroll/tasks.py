"""
Tâches Celery du module paie.
"""
from celery import shared_task


@shared_task(bind=True, max_retries=3)
def generate_payslip_pdf(self: object, payslip_id: int) -> dict:
    """
    Générer le PDF d'un bulletin de paie de manière asynchrone.

    Args:
        payslip_id: Identifiant du bulletin de paie

    Returns:
        Dictionnaire avec le statut et le chemin du fichier
    """
    from .models import Payslip
    from .services_pdf import PayslipPDFService

    try:
        payslip = Payslip.objects.select_related("employee").get(pk=payslip_id)
    except Payslip.DoesNotExist:
        return {"status": "error", "message": f"Bulletin {payslip_id} introuvable."}

    try:
        pdf_service = PayslipPDFService()
        pdf_path = pdf_service.generate(payslip)
        return {"status": "success", "pdf_path": str(pdf_path)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # type: ignore[attr-defined]


@shared_task
def generate_monthly_payslips_pdf(month: int, year: int) -> dict:
    """
    Générer les PDF pour tous les bulletins d'un mois.

    Args:
        month: Mois (1-12)
        year: Année

    Returns:
        Dictionnaire avec le nombre de PDF générés
    """
    from .models import Payslip

    payslips = Payslip.objects.filter(month=month, year=year, pdf_file="")
    count = 0
    for payslip in payslips:
        generate_payslip_pdf.delay(payslip.id)
        count += 1

    return {
        "status": "success",
        "message": f"{count} tâche(s) de génération PDF lancée(s).",
    }
