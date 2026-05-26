"""
Modèle SystemConfig — paramètres système stockés en base de données.
Aucune valeur métier (taux, plafonds) ne doit être codée en dur.
Tout passe par cette table.
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemConfig(models.Model):
    """
    Configuration système clé-valeur.

    Stocke tous les paramètres légaux et métier :
    taux de cotisations, plafonds, barèmes IRSA, taux TVA, etc.
    Permet de modifier les valeurs sans redéploiement.
    """

    key = models.CharField(
        _("Clé"),
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Identifiant unique du paramètre (ex: SME_AMOUNT)"),
    )
    value = models.DecimalField(
        _("Valeur"),
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Valeur numérique du paramètre"),
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Description du paramètre et de son utilisation"),
    )
    updated_at = models.DateTimeField(
        _("Dernière modification"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Configuration système")
        verbose_name_plural = _("Configurations système")
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key} = {self.value}"

    @classmethod
    def get_value(cls, key: str, default: Decimal | None = None) -> Decimal:
        """
        Récupérer la valeur d'un paramètre par sa clé.

        Args:
            key: Clé du paramètre (ex: 'SME_AMOUNT')
            default: Valeur par défaut si la clé n'existe pas

        Returns:
            La valeur décimale du paramètre

        Raises:
            KeyError: Si la clé n'existe pas et aucun défaut fourni
        """
        try:
            config = cls.objects.get(key=key)
            return config.value
        except cls.DoesNotExist:
            if default is not None:
                return default
            raise KeyError(
                f"Le paramètre système '{key}' n'existe pas. "
                f"Veuillez l'ajouter via l'admin ou la migration de données."
            )
