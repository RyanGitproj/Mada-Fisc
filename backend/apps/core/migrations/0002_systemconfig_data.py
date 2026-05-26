"""
Data migration — valeurs légales Madagascar 2026.
Source : Loi de Finances n° 2025-021, décret mars 2026.
"""
from decimal import Decimal
from django.db import migrations


def load_default_config(apps: object, schema_editor: object) -> None:
    SystemConfig = apps.get_model("core", "SystemConfig")

    configs = [
        # --- Cotisations sociales ---
        {
            "key": "SME_AMOUNT",
            "value": Decimal("300000"),
            "description": "Salaire Minimum d'Embauche (SME) — revalorisation +14% LF 2026",
        },
        {
            "key": "CNAPS_CEILING_MULTIPLIER",
            "value": Decimal("8"),
            "description": "Multiplicateur du SME pour le plafond de cotisations (plafond = 8 × SME = 2 400 000 Ar)",
        },
        {
            "key": "CNAPS_EMPLOYEE_RATE",
            "value": Decimal("0.01"),
            "description": "Taux de cotisation CNaPS part salarié (1%)",
        },
        {
            "key": "CNAPS_EMPLOYER_RATE",
            "value": Decimal("0.13"),
            "description": "Taux de cotisation CNaPS part employeur (13%)",
        },
        {
            "key": "OSTIE_EMPLOYEE_RATE",
            "value": Decimal("0.01"),
            "description": "Taux de cotisation OSTIE/AMIT part salarié (1%)",
        },
        {
            "key": "OSTIE_EMPLOYER_RATE",
            "value": Decimal("0.05"),
            "description": "Taux de cotisation OSTIE/AMIT part employeur (5%)",
        },
        {
            "key": "FMFP_EMPLOYEE_RATE",
            "value": Decimal("0.01"),
            "description": "Taux de cotisation FMFP part salarié (1%)",
        },
        {
            "key": "FMFP_EMPLOYER_RATE",
            "value": Decimal("0.01"),
            "description": "Taux de cotisation FMFP part employeur (1%)",
        },
        {
            "key": "DEFAULT_ORGANISM_SANITAIRE",
            "value": Decimal("1"),
            "description": "Organisme sanitaire par défaut : 1=OSTIE, 2=AMIT, 3=ESIA, 4=FUNHECE",
        },
        # --- TVA ---
        {
            "key": "TVA_RATE",
            "value": Decimal("0.20"),
            "description": "Taux de TVA (20%, inchangé)",
        },
        # --- IRSA ---
        {
            "key": "IRSA_MINIMUM_PERCEPTION",
            "value": Decimal("3000"),
            "description": "Minimum de perception IRSA (3 000 Ar — LF 2026, était 2 000 Ar)",
        },
        {
            "key": "IRSA_REDUCTION_PAR_CHARGE",
            "value": Decimal("2000"),
            "description": "Réduction d'IRSA par personne à charge (2 000 Ar)",
        },
        # --- Tranches IRSA 2026 ---
        {
            "key": "IRSA_BRACKET_1_MIN",
            "value": Decimal("0"),
            "description": "Tranche 1 IRSA — seuil minimum",
        },
        {
            "key": "IRSA_BRACKET_1_MAX",
            "value": Decimal("350000"),
            "description": "Tranche 1 IRSA — seuil maximum (≤ 350 000 Ar)",
        },
        {
            "key": "IRSA_BRACKET_1_RATE",
            "value": Decimal("0"),
            "description": "Tranche 1 IRSA — taux (0%)",
        },
        {
            "key": "IRSA_BRACKET_2_MIN",
            "value": Decimal("350000"),
            "description": "Tranche 2 IRSA — seuil minimum (borne inférieure de la tranche 350 001 – 400 000)",
        },
        {
            "key": "IRSA_BRACKET_2_MAX",
            "value": Decimal("400000"),
            "description": "Tranche 2 IRSA — seuil maximum (350 001 – 400 000 Ar)",
        },
        {
            "key": "IRSA_BRACKET_2_RATE",
            "value": Decimal("0.05"),
            "description": "Tranche 2 IRSA — taux (5%)",
        },
        {
            "key": "IRSA_BRACKET_3_MIN",
            "value": Decimal("400000"),
            "description": "Tranche 3 IRSA — seuil minimum (borne inférieure de la tranche 400 001 – 500 000)",
        },
        {
            "key": "IRSA_BRACKET_3_MAX",
            "value": Decimal("500000"),
            "description": "Tranche 3 IRSA — seuil maximum (400 001 – 500 000 Ar)",
        },
        {
            "key": "IRSA_BRACKET_3_RATE",
            "value": Decimal("0.10"),
            "description": "Tranche 3 IRSA — taux (10%)",
        },
        {
            "key": "IRSA_BRACKET_4_MIN",
            "value": Decimal("500000"),
            "description": "Tranche 4 IRSA — seuil minimum (borne inférieure de la tranche 500 001 – 600 000)",
        },
        {
            "key": "IRSA_BRACKET_4_MAX",
            "value": Decimal("600000"),
            "description": "Tranche 4 IRSA — seuil maximum (500 001 – 600 000 Ar)",
        },
        {
            "key": "IRSA_BRACKET_4_RATE",
            "value": Decimal("0.15"),
            "description": "Tranche 4 IRSA — taux (15%)",
        },
        {
            "key": "IRSA_BRACKET_5_MIN",
            "value": Decimal("600000"),
            "description": "Tranche 5 IRSA — seuil minimum (borne inférieure de la tranche 600 001 – 4 000 000)",
        },
        {
            "key": "IRSA_BRACKET_5_MAX",
            "value": Decimal("4000000"),
            "description": "Tranche 5 IRSA — seuil maximum (600 001 – 4 000 000 Ar)",
        },
        {
            "key": "IRSA_BRACKET_5_RATE",
            "value": Decimal("0.20"),
            "description": "Tranche 5 IRSA — taux (20%)",
        },
        {
            "key": "IRSA_BRACKET_6_MIN",
            "value": Decimal("4000000"),
            "description": "Tranche 6 IRSA — seuil minimum (borne inférieure de la tranche > 4 000 000)",
        },
        {
            "key": "IRSA_BRACKET_6_MAX",
            "value": Decimal("999999999"),
            "description": "Tranche 6 IRSA — seuil maximum (> 4 000 000 Ar, valeur sentinelle)",
        },
        {
            "key": "IRSA_BRACKET_6_RATE",
            "value": Decimal("0.25"),
            "description": "Tranche 6 IRSA — taux (25%)",
        },
    ]

    for config_data in configs:
        SystemConfig.objects.update_or_create(
            key=config_data["key"],
            defaults={
                "value": config_data["value"],
                "description": config_data["description"],
            },
        )


def reverse_default_config(apps: object, schema_editor: object) -> None:
    SystemConfig = apps.get_model("core", "SystemConfig")
    SystemConfig.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_default_config, reverse_default_config),
    ]
