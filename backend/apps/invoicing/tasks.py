"""
Tâches Celery du module facturation.
"""
from celery import shared_task


@shared_task
def mark_overdue_invoices() -> dict:
    """
    Marquer les factures en retard (exécuté par Celery Beat).
    Planifié : chaque 1er du mois à 08:00 heure Madagascar (UTC+3).
    """
    from .services import InvoiceService
    from .repositories import ClientRepository, InvoiceRepository
    from apps.invoicing.services import InvoiceCalculationService

    invoice_service = InvoiceService(
        invoice_repo=InvoiceRepository(),
        client_repo=ClientRepository(),
        calc_service=InvoiceCalculationService(),
    )

    count = invoice_service.mark_overdue_invoices()
    return {
        "status": "success",
        "message": f"{count} facture(s) marquée(s) en retard.",
    }


@shared_task(bind=True, max_retries=3)
def generate_invoice_pdf(self: object, invoice_id: int) -> dict:
    """
    Générer le PDF d'une facture de manière asynchrone.
    """
    from .models import Invoice

    try:
        invoice = Invoice.objects.select_related("client").get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return {"status": "error", "message": f"Facture {invoice_id} introuvable."}

    try:
        from apps.invoicing.services_pdf import InvoicePDFService
        pdf_service = InvoicePDFService()
        pdf_path = pdf_service.generate(invoice)
        return {"status": "success", "pdf_path": str(pdf_path)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # type: ignore[attr-defined]


@shared_task
def send_overdue_reminders() -> dict:
    """
    Envoyer des rappels pour les factures en retard.
    """
    from .models import Invoice
    from django.core.mail import send_mail

    overdue_invoices = Invoice.objects.filter(
        status=Invoice.Status.OVERDUE,
    ).select_related("client")

    count = 0
    for invoice in overdue_invoices:
        if invoice.client.email:
            try:
                send_mail(
                    subject=f"Rappel : Facture {invoice.invoice_number} en retard",
                    message=(
                        f"Bonjour {invoice.client.company_name},\n\n"
                        f"La facture {invoice.invoice_number} d'un montant de "
                        f"{invoice.amount_ttc} Ar TTC était due le {invoice.due_date}.\n\n"
                        f"Merci de régler cette facture dans les meilleurs délais.\n\n"
                        f"Cordialement."
                    ),
                    from_email="noreply@mada-fisc.mg",
                    recipient_list=[invoice.client.email],
                    fail_silently=True,
                )
                count += 1
            except Exception:
                continue

    return {
        "status": "success",
        "message": f"{count} rappel(s) envoyé(s).",
    }
