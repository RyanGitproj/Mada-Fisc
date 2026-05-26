"""
Serializers du module facturation.
Séparés en InputSerializer (validation) et OutputSerializer (présentation).
"""
from decimal import Decimal

from rest_framework import serializers

from .models import Client, Invoice


# --- Client Serializers ---

class ClientInputSerializer(serializers.Serializer):
    """Serializer de validation pour la création/mise à jour d'un client."""
    company_name = serializers.CharField(max_length=200)
    nif = serializers.CharField(max_length=30, required=False, default="")
    stat = serializers.CharField(max_length=30, required=False, default="")
    email = serializers.EmailField(required=False, default="")
    phone = serializers.CharField(max_length=20, required=False, default="")
    address = serializers.CharField(required=False, default="")
    is_active = serializers.BooleanField(default=True)


class ClientOutputSerializer(serializers.ModelSerializer):
    """Serializer de présentation pour un client."""

    class Meta:
        model = Client
        fields = [
            "id", "company_name", "nif", "stat", "email",
            "phone", "address", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# --- Invoice Serializers ---

class InvoiceCreateInputSerializer(serializers.Serializer):
    """Serializer de validation pour la création d'une facture."""
    client_id = serializers.IntegerField(min_value=1)
    amount_ht = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0")
    )
    due_date = serializers.DateField()
    issue_date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, default="")


class InvoiceStatusInputSerializer(serializers.Serializer):
    """Serializer de validation pour le changement de statut."""
    status = serializers.ChoiceField(choices=Invoice.Status.choices)


class InvoiceOutputSerializer(serializers.ModelSerializer):
    """Serializer de présentation pour une facture."""
    client_name = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            "id", "client", "client_name", "invoice_number",
            "issue_date", "due_date", "amount_ht", "tva_amount",
            "amount_ttc", "status", "is_overdue", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "invoice_number", "tva_amount", "amount_ttc",
            "created_at", "updated_at",
        ]

    def get_client_name(self, obj: Invoice) -> str:
        return obj.client.company_name


class InvoiceDetailOutputSerializer(InvoiceOutputSerializer):
    """Serializer détaillé pour une facture."""

    class Meta(InvoiceOutputSerializer.Meta):
        fields = InvoiceOutputSerializer.Meta.fields + ["pdf_file"]
