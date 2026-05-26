"""
Tests unitaires du service de calcul de paie.

Ces tests valident le calcul IRSA 2026 selon le barème officiel
de la Loi de Finances n° 2025-021.

Les tests sont PUREMENT UNITAIRES : aucune base de données nécessaire.
Les paramètres légaux sont passés directement en arguments.
"""
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from apps.payroll.services import (
    IRSABracket,
    PayrollCalculationService,
    PayrollResult,
)


# --- Barème IRSA 2026 (Loi de Finances n° 2025-021) ---
# Les min_values sont les bornes inférieures des tranches :
# Tranche 2 couvre 350 001 – 400 000 → min = 350 000
# Tranche 3 couvre 400 001 – 500 000 → min = 400 000
# etc.
IRSA_BRACKETS_2026 = [
    IRSABracket(tranche=1, min_value=Decimal("0"),      max_value=Decimal("350000"),  rate=Decimal("0")),
    IRSABracket(tranche=2, min_value=Decimal("350000"), max_value=Decimal("400000"),  rate=Decimal("0.05")),
    IRSABracket(tranche=3, min_value=Decimal("400000"), max_value=Decimal("500000"),  rate=Decimal("0.10")),
    IRSABracket(tranche=4, min_value=Decimal("500000"), max_value=Decimal("600000"),  rate=Decimal("0.15")),
    IRSABracket(tranche=5, min_value=Decimal("600000"), max_value=Decimal("4000000"), rate=Decimal("0.20")),
    IRSABracket(tranche=6, min_value=Decimal("4000000"), max_value=Decimal("999999999"), rate=Decimal("0.25")),
]

# Paramètres légaux 2026
CNAPS_RATE = Decimal("0.01")
OSTIE_RATE = Decimal("0.01")
FMFP_RATE = Decimal("0.01")
PLAFOND = Decimal("2400000")  # 8 × SME (300 000)
IRSA_MINIMUM = Decimal("3000")
IRSA_REDUCTION_PAR_CHARGE = Decimal("2000")


class TestPayrollCalculationService:
    """Tests du service de calcul de paie."""

    def setup_method(self) -> None:
        """Configurer le service de calcul avec les paramètres 2026."""
        self.service = PayrollCalculationService(config_repo=MagicMock())

    def _calculate(
        self,
        gross_salary: Decimal,
        dependants: int = 0,
    ) -> PayrollResult:
        """Calculer la paie avec les paramètres légaux 2026 en dur."""
        return self.service.calculate(
            gross_salary=gross_salary,
            dependants=dependants,
            cnaps_rate=CNAPS_RATE,
            ostie_rate=OSTIE_RATE,
            fmfp_rate=FMFP_RATE,
            plafond=PLAFOND,
            irsa_brackets=IRSA_BRACKETS_2026,
            irsa_minimum=IRSA_MINIMUM,
            irsa_reduction_par_charge=IRSA_REDUCTION_PAR_CHARGE,
        )

    # --- Cas 1 : Employé exonéré (brut ≤ 350 000, base IRSA ≤ 350 000) ---

    def test_exonere_350000(self) -> None:
        """
        Brut = 350 000 Ar → exonéré d'IRSA.

        CNaPS = 350 000 × 1% = 3 500
        OSTIE = 350 000 × 1% = 3 500
        FMFP  = 350 000 × 1% = 3 500
        Base IRSA brut = 350 000 - 3 500 - 3 500 - 3 500 = 339 500
        Base IRSA = floor(339 500 / 100) × 100 = 339 500 (déjà multiple de 100)
        IRSA = 0 (base ≤ 350 000)
        Net = 350 000 - 3 500 - 3 500 - 3 500 - 0 = 339 500
        """
        result = self._calculate(Decimal("350000"))

        assert result.cnaps_deduction == Decimal("3500")
        assert result.ostie_deduction == Decimal("3500")
        assert result.fmfp_deduction == Decimal("3500")
        assert result.base_irsa == Decimal("339500")
        assert result.irsa_final == Decimal("0")
        assert result.net_salary == Decimal("339500")

    # --- Cas 2 : Multi-tranches (brut = 500 000) ---

    def test_multi_tranches_500000(self) -> None:
        """
        Brut = 500 000 Ar → multi-tranches.

        CNaPS = 500 000 × 1% = 5 000
        OSTIE = 500 000 × 1% = 5 000
        FMFP  = 500 000 × 1% = 5 000
        Base IRSA brut = 500 000 - 5 000 - 5 000 - 5 000 = 485 000
        Base IRSA = floor(485 000 / 100) × 100 = 485 000
        IRSA :
          Tranche 1 (0 – 350 000) : 0%
          Tranche 2 (350 001 – 400 000) : 50 000 × 5% = 2 500
          Tranche 3 (400 001 – 485 000) : 85 000 × 10% = 8 500
          Total IRSA brut = 2 500 + 8 500 = 11 000
          IRSA final = 11 000 (> minimum 3 000)
          Net = 500 000 - 5 000 - 5 000 - 5 000 - 11 000 = 474 000
        """
        result = self._calculate(Decimal("500000"))

        assert result.cnaps_deduction == Decimal("5000")
        assert result.ostie_deduction == Decimal("5000")
        assert result.fmfp_deduction == Decimal("5000")
        assert result.base_irsa_brut == Decimal("485000")
        assert result.base_irsa == Decimal("485000")
        assert result.irsa_brut == Decimal("11000")
        assert result.irsa_final == Decimal("11000")
        assert result.net_salary == Decimal("474000")

    # --- Cas 3 : Haut salaire (brut = 1 500 000) ---

    def test_haut_salaire_1500000(self) -> None:
        """
        Brut = 1 500 000 Ar.

        CNaPS = 1 500 000 × 1% = 15 000 (< plafond)
        OSTIE = 1 500 000 × 1% = 15 000
        FMFP  = 1 500 000 × 1% = 15 000
        Base IRSA brut = 1 500 000 - 15 000 - 15 000 - 15 000 = 1 455 000
        Base IRSA = floor(1 455 000 / 100) × 100 = 1 455 000
        IRSA :
          Tranche 2 : 50 000 × 5% = 2 500
          Tranche 3 : 100 000 × 10% = 10 000
          Tranche 4 : 100 000 × 15% = 15 000
          Tranche 5 : 855 000 × 20% = 171 000
          Total = 2 500 + 10 000 + 15 000 + 171 000 = 198 500
        Net = 1 500 000 - 15 000 - 15 000 - 15 000 - 198 500 = 1 256 500
        """
        result = self._calculate(Decimal("1500000"))

        assert result.cnaps_deduction == Decimal("15000")
        assert result.ostie_deduction == Decimal("15000")
        assert result.fmfp_deduction == Decimal("15000")
        assert result.base_irsa == Decimal("1455000")
        assert result.irsa_final == Decimal("198500")
        assert result.net_salary == Decimal("1256500")

    # --- Cas 4 : Personne avec 2 enfants à charge, brut = 500 000 ---

    def test_reduction_2_charges_500000(self) -> None:
        """
        Brut = 500 000 Ar, 2 personnes à charge.

        IRSA brut = 11 000 (même calcul que le cas 2)
        Réduction = 2 × 2 000 = 4 000
        IRSA après réduction = 11 000 - 4 000 = 7 000
        IRSA final = 7 000 (> minimum 3 000)
        Net = 500 000 - 5 000 - 5 000 - 5 000 - 7 000 = 478 000
        """
        result = self._calculate(Decimal("500000"), dependants=2)

        assert result.irsa_brut == Decimal("11000")
        assert result.irsa_reduction == Decimal("4000")
        assert result.irsa_final == Decimal("7000")
        assert result.net_salary == Decimal("478000")

    # --- Cas 5 : Test plafond — brut = 3 000 000 ---

    def test_plafond_cotisations_3000000(self) -> None:
        """
        Brut = 3 000 000 Ar → CNaPS calculé sur le plafond 2 400 000.

        CNaPS = MIN(3 000 000, 2 400 000) × 1% = 24 000
        OSTIE = 24 000
        FMFP  = 24 000
        Base IRSA brut = 3 000 000 - 24 000 - 24 000 - 24 000 = 2 928 000
        Base IRSA = 2 928 000
        """
        result = self._calculate(Decimal("3000000"))

        assert result.cnaps_deduction == Decimal("24000")
        assert result.ostie_deduction == Decimal("24000")
        assert result.fmfp_deduction == Decimal("24000")
        assert result.base_irsa_brut == Decimal("2928000")
        assert result.net_salary > Decimal("0")

    # --- Cas 6 : Minimum de perception ---

    def test_minimum_perception_360000(self) -> None:
        """
        Brut = 360 000 Ar → base_irsa < 350 000 → exonéré.

        CNaPS = 3 600
        OSTIE = 3 600
        FMFP  = 3 600
        Base IRSA brut = 360 000 - 3 600 - 3 600 - 3 600 = 349 200
        Base IRSA = floor(349 200 / 100) × 100 = 349 200
        349 200 ≤ 350 000 → exonéré → IRSA = 0

        Pour un cas réel de minimum de perception,
        il faut base_irsa > 350 000 mais IRSA calculé < 3 000 :
        brut = 361 000 → déductions = 3 × 3 610 = 10 830
        base_irsa_brut = 361 000 - 10 830 = 350 170
        base_irsa = floor(350 170 / 100) × 100 = 350 100
        IRSA : (350 100 - 350 000) × 5% = 100 × 0.05 = 5.00
        Minimum de perception = 3 000 → IRSA final = 3 000
        """
        # Avec brut = 360 000 : base_irsa = 349 200 < 350 000 → exonéré
        result = self._calculate(Decimal("360000"))
        assert result.base_irsa == Decimal("349200")
        assert result.irsa_final == Decimal("0")

        # Avec brut = 361 000 : base_irsa = 350 100 > 350 000 mais IRSA < 3 000
        result2 = self._calculate(Decimal("361000"))
        assert result2.base_irsa == Decimal("350100")
        assert result2.irsa_brut < IRSA_MINIMUM
        assert result2.irsa_final == IRSA_MINIMUM

    # --- Tests supplémentaires ---

    def test_salaire_negatif_rejete(self) -> None:
        """Un salaire négatif doit lever une exception."""
        with pytest.raises(Exception):
            self._calculate(Decimal("-100000"))

    def test_dependants_negatifs_rejetes(self) -> None:
        """Un nombre de personnes à charge négatif doit lever une exception."""
        with pytest.raises(Exception):
            self._calculate(Decimal("500000"), dependants=-1)

    def test_arrondi_centaine_inferieure(self) -> None:
        """Vérifier l'arrondi à la centaine inférieure."""
        assert self.service._arrondir_centaine_inferieure(
            Decimal("485500")
        ) == Decimal("485500")
        assert self.service._arrondir_centaine_inferieure(
            Decimal("485599")
        ) == Decimal("485500")
        assert self.service._arrondir_centaine_inferieure(
            Decimal("485601")
        ) == Decimal("485600")

    def test_cotisation_plafonnée(self) -> None:
        """Au-delà du plafond, les cotisations sont calculées sur le plafond."""
        result = self._calculate(Decimal("5000000"))
        # 5 000 000 > plafond 2 400 000
        assert result.cnaps_deduction == Decimal("24000")  # 2 400 000 × 1%
        assert result.ostie_deduction == Decimal("24000")
        assert result.fmfp_deduction == Decimal("24000")

    def test_tranche_superieure_4millions(self) -> None:
        """Salaire très élevé atteignant la tranche 6 (> 4 000 000)."""
        result = self._calculate(Decimal("5000000"))
        assert result.base_irsa > Decimal("4000000")
        # Vérifier que la tranche 6 (25%) est appliquée
        tranche_6 = [d for d in result.bracket_details if d["tranche"] == 6]
        assert len(tranche_6) == 1
        assert Decimal(tranche_6[0]["taux"]) == Decimal("0.25")
        assert Decimal(tranche_6[0]["montant_imposable"]) > Decimal("0")
