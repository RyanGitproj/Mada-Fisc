"""
Migration initiale — création du modèle SystemConfig avec les données légales Madagascar 2026.
"""
from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SystemConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(db_index=True, help_text="Identifiant unique du paramètre (ex: SME_AMOUNT)", max_length=100, unique=True, verbose_name="Clé")),
                ("value", models.DecimalField(decimal_places=4, help_text="Valeur numérique du paramètre", max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal("0"))], verbose_name="Valeur")),
                ("description", models.TextField(help_text="Description du paramètre et de son utilisation", verbose_name="Description")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Dernière modification")),
            ],
            options={
                "verbose_name": "Configuration système",
                "verbose_name_plural": "Configurations système",
                "ordering": ["key"],
            },
        ),
    ]
