"""
Dépôt SystemConfig — abstraction d'accès aux données de configuration.
"""
from decimal import Decimal
from typing import Dict, Optional

from .models import SystemConfig


class SystemConfigRepository:
    """Dépôt pour l'accès aux paramètres système."""

    def get_by_key(self, key: str) -> Optional[SystemConfig]:
        """Récupérer un paramètre par sa clé."""
        try:
            return SystemConfig.objects.get(key=key)
        except SystemConfig.DoesNotExist:
            return None

    def get_value(self, key: str, default: Optional[Decimal] = None) -> Decimal:
        """Récupérer la valeur d'un paramètre."""
        config = self.get_by_key(key)
        if config is not None:
            return config.value
        if default is not None:
            return default
        raise KeyError(f"Paramètre système '{key}' introuvable.")

    def get_all_as_dict(self) -> Dict[str, Decimal]:
        """Récupérer tous les paramètres sous forme de dictionnaire."""
        return {
            config.key: config.value
            for config in SystemConfig.objects.all()
        }

    def get_multiple(self, keys: list[str]) -> Dict[str, Decimal]:
        """Récupérer plusieurs paramètres en une seule requête."""
        configs = SystemConfig.objects.filter(key__in=keys)
        return {config.key: config.value for config in configs}

    def set_value(self, key: str, value: Decimal) -> SystemConfig:
        """Mettre à jour ou créer un paramètre."""
        config, created = SystemConfig.objects.update_or_create(
            key=key,
            defaults={"value": value},
        )
        return config

    def get_irsa_brackets(self) -> list[Dict[str, Decimal]]:
        """
        Récupérer les tranches IRSA depuis la configuration système.
        Les tranches sont stockées comme :
        IRSA_BRACKET_1_MIN, IRSA_BRACKET_1_MAX, IRSA_BRACKET_1_RATE, etc.
        """
        brackets = []
        for i in range(1, 7):
            prefix = f"IRSA_BRACKET_{i}"
            min_key = f"{prefix}_MIN"
            max_key = f"{prefix}_MAX"
            rate_key = f"{prefix}_RATE"

            min_val = self.get_value(min_key)
            max_val = self.get_value(max_key)
            rate_val = self.get_value(rate_key)

            brackets.append({
                "tranche": i,
                "min": min_val,
                "max": max_val,
                "rate": rate_val,
            })

        return brackets
