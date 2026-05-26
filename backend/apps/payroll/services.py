"""
Services du module paie — logique métier pure.

PayrollCalculationService : calcul IRSA 2026, cotisations sociales, salaire net.
PayslipService : orchestration de la génération des bulletins de paie.

Règles de calcul (Section 1 du cahier des charges) :
1. Charges salariales = MIN(brut, plafond) pour CNaPS, OSTIE, FMFP
2. cnaps = MIN(brut, plafond) × taux_salarie_cnaps
3. ostie = MIN(brut, plafond) × taux_salarie_ostie
4. fmfp = MIN(brut, plafond) × taux_salarie_fmfp
5. base_irsa_avant_arrondi = brut − cnaps − ostie − fmfp
6. base_irsa = floor(base_irsa_avant_arrondi / 100) × 100  ← arrondi centaine inférieure
7. Calcul par tranches progressives (6 tranches IRSA 2026)
8. Réduction : 2 000 Ar par personne_à_charge sur l'IRSA calculé
9. irsa_final = MAX(irsa_après_réduction, 3 000) si base_irsa > 350 000, sinon 0
10. net_salary = brut − cnaps − ostie − fmfp − irsa_final
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_DOWN
from typing import List

from apps.core.exceptions import (
    DuplicatePayslipError,
    EmployeeNotFoundError,
    InvalidPayrollPeriodError,
    PayrollCalculationError,
)
from apps.core.repositories import SystemConfigRepository
from apps.payroll.repositories import EmployeeRepository, PayslipRepository


@dataclass
class IRSABracket:
    """Tranche du barème IRSA."""
    tranche: int
    min_value: Decimal
    max_value: Decimal
    rate: Decimal


@dataclass
class PayrollResult:
    """Résultat du calcul de paie pour un employé."""
    gross_salary: Decimal
    cnaps_deduction: Decimal
    ostie_deduction: Decimal
    fmfp_deduction: Decimal
    base_irsa_brut: Decimal
    base_irsa: Decimal
    irsa_brut: Decimal
    irsa_reduction: Decimal
    irsa_final: Decimal
    net_salary: Decimal
    dependants_count: int
    bracket_details: List[dict] = field(default_factory=list)


class PayrollCalculationService:
    """
    Service de calcul de la paie malgache.

    Ce service est pur : il n'a aucune dépendance Django ni HTTP.
    Il peut être testé unitairement sans base de données.
    Tous les paramètres légaux sont passés en argument ou récupérés
    via le SystemConfigRepository.
    """

    def __init__(self, config_repo: SystemConfigRepository | None = None) -> None:
        """
        Initialiser le service de calcul.

        Args:
            config_repo: Dépôt de configuration système.
                         Si None, un nouveau dépôt sera créé.
        """
        self._config_repo = config_repo or SystemConfigRepository()

    def calculate(
        self,
        gross_salary: Decimal,
        dependants: int = 0,
        cnaps_rate: Decimal | None = None,
        ostie_rate: Decimal | None = None,
        fmfp_rate: Decimal | None = None,
        plafond: Decimal | None = None,
        irsa_brackets: list[IRSABracket] | None = None,
        irsa_minimum: Decimal | None = None,
        irsa_reduction_par_charge: Decimal | None = None,
    ) -> PayrollResult:
        """
        Calculer la paie complète pour un salaire brut donné.

        Args:
            gross_salary: Salaire brut mensuel en Ariary
            dependants: Nombre de personnes à charge
            cnaps_rate: Taux CNaPS salarié (défaut: depuis SystemConfig)
            ostie_rate: Taux OSTIE salarié (défaut: depuis SystemConfig)
            fmfp_rate: Taux FMFP salarié (défaut: depuis SystemConfig)
            plafond: Plafond de cotisations (défaut: SME × 8)
            irsa_brackets: Tranches IRSA (défaut: depuis SystemConfig)
            irsa_minimum: Minimum de perception IRSA (défaut: depuis SystemConfig)
            irsa_reduction_par_charge: Réduction par charge (défaut: depuis SystemConfig)

        Returns:
            PayrollResult avec tous les montants calculés
        """
        if gross_salary < 0:
            raise PayrollCalculationError(
                "Le salaire brut ne peut pas être négatif."
            )

        if dependants < 0:
            raise PayrollCalculationError(
                "Le nombre de personnes à charge ne peut pas être négatif."
            )

        # Récupérer les paramètres (depuis SystemConfig ou arguments)
        cnaps_rate = cnaps_rate or self._config_repo.get_value("CNAPS_EMPLOYEE_RATE")
        ostie_rate = ostie_rate or self._config_repo.get_value("OSTIE_EMPLOYEE_RATE")
        fmfp_rate = fmfp_rate or self._config_repo.get_value("FMFP_EMPLOYEE_RATE")
        irsa_minimum = irsa_minimum or self._config_repo.get_value("IRSA_MINIMUM_PERCEPTION")
        irsa_reduction_par_charge = (
            irsa_reduction_par_charge
            or self._config_repo.get_value("IRSA_REDUCTION_PAR_CHARGE")
        )

        if plafond is None:
            sme = self._config_repo.get_value("SME_AMOUNT")
            multiplier = self._config_repo.get_value("CNAPS_CEILING_MULTIPLIER")
            plafond = sme * multiplier

        if irsa_brackets is None:
            irsa_brackets = self._get_irsa_brackets()

        # --- Étape 1-4 : Cotisations sociales (plafonnées) ---
        base_cotisations = min(gross_salary, plafond)
        cnaps_deduction = self._calculate_deduction(base_cotisations, cnaps_rate)
        ostie_deduction = self._calculate_deduction(base_cotisations, ostie_rate)
        fmfp_deduction = self._calculate_deduction(base_cotisations, fmfp_rate)

        # --- Étape 5 : Base IRSA avant arrondi ---
        base_irsa_brut = (
            gross_salary - cnaps_deduction - ostie_deduction - fmfp_deduction
        )

        # --- Étape 6 : Arrondi centaine inférieure ---
        base_irsa = self._arrondir_centaine_inferieure(base_irsa_brut)

        # --- Étape 7 : Calcul IRSA par tranches progressives ---
        irsa_brut, bracket_details = self._calculate_irsa_by_brackets(
            base_irsa, irsa_brackets
        )

        # --- Étape 8 : Réduction pour personnes à charge ---
        irsa_reduction = Decimal(dependants) * irsa_reduction_par_charge
        irsa_apres_reduction = max(irsa_brut - irsa_reduction, Decimal("0"))

        # --- Étape 9 : Minimum de perception ---
        if base_irsa > Decimal("350000"):
            irsa_final = max(irsa_apres_reduction, irsa_minimum)
        else:
            irsa_final = Decimal("0")

        # --- Étape 10 : Salaire net ---
        net_salary = (
            gross_salary
            - cnaps_deduction
            - ostie_deduction
            - fmfp_deduction
            - irsa_final
        )

        return PayrollResult(
            gross_salary=gross_salary,
            cnaps_deduction=cnaps_deduction,
            ostie_deduction=ostie_deduction,
            fmfp_deduction=fmfp_deduction,
            base_irsa_brut=base_irsa_brut,
            base_irsa=base_irsa,
            irsa_brut=irsa_brut,
            irsa_reduction=irsa_reduction,
            irsa_final=irsa_final,
            net_salary=net_salary,
            dependants_count=dependants,
            bracket_details=bracket_details,
        )

    def _calculate_deduction(
        self, base: Decimal, rate: Decimal
    ) -> Decimal:
        """Calculer une cotisation : base × taux."""
        return (base * rate).quantize(Decimal("0.01"))

    def _arrondir_centaine_inferieure(self, value: Decimal) -> Decimal:
        """Arrondir à la centaine inférieure : floor(value / 100) × 100."""
        centaines = (value / Decimal("100")).to_integral_value(rounding=ROUND_DOWN)
        return centaines * Decimal("100")

    def _calculate_irsa_by_brackets(
        self,
        base_irsa: Decimal,
        brackets: list[IRSABracket],
    ) -> tuple[Decimal, list[dict]]:
        """
        Calculer l'IRSA par tranches progressives.

        Returns:
            Tuple (montant_total, détail_par_tranche)
        """
        total = Decimal("0")
        details: list[dict] = []

        for bracket in brackets:
            if base_irsa <= bracket.min_value:
                # La base imposable est en dessous de cette tranche
                details.append({
                    "tranche": bracket.tranche,
                    "min": str(bracket.min_value),
                    "max": str(bracket.max_value),
                    "taux": str(bracket.rate),
                    "montant_imposable": "0",
                    "impot": "0",
                })
                continue

            # La part imposable dans cette tranche
            upper_bound = min(base_irsa, bracket.max_value)
            montant_imposable = upper_bound - bracket.min_value
            impot_tranche = (montant_imposable * bracket.rate).quantize(
                Decimal("0.01")
            )
            total += impot_tranche

            details.append({
                "tranche": bracket.tranche,
                "min": str(bracket.min_value),
                "max": str(bracket.max_value),
                "taux": str(bracket.rate),
                "montant_imposable": str(montant_imposable),
                "impot": str(impot_tranche),
            })

        return total, details

    def _get_irsa_brackets(self) -> list[IRSABracket]:
        """Récupérer les tranches IRSA depuis SystemConfig."""
        brackets_data = self._config_repo.get_irsa_brackets()
        return [
            IRSABracket(
                tranche=b["tranche"],
                min_value=b["min"],
                max_value=b["max"],
                rate=b["rate"],
            )
            for b in brackets_data
        ]


class PayslipService:
    """
    Service d'orchestration de la génération des bulletins de paie.

    Coordonne le calcul, la persistance et la génération PDF.
    Dépend du PayslipRepository et du PayrollCalculationService.
    """

    def __init__(
        self,
        payslip_repo: PayslipRepository,
        employee_repo: EmployeeRepository,
        calc_service: PayrollCalculationService,
    ) -> None:
        self._payslip_repo = payslip_repo
        self._employee_repo = employee_repo
        self._calc_service = calc_service

    def generate_payslip(
        self, employee_id: int, month: int, year: int
    ) -> PayrollResult:
        """
        Générer un bulletin de paie pour un employé et une période.

        Args:
            employee_id: Identifiant de l'employé
            month: Mois (1-12)
            year: Année

        Returns:
            PayrollResult avec les montants calculés

        Raises:
            EmployeeNotFoundError: Si l'employé n'existe pas
            DuplicatePayslipError: Si un bulletin existe déjà
            InvalidPayrollPeriodError: Si la période est invalide
        """
        # Validation de la période
        self._validate_period(month, year)

        # Vérifier que l'employé existe
        employee = self._employee_repo.get_active_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFoundError(employee_id)

        # Vérifier l'absence de doublon
        if self._payslip_repo.exists_for_period(employee_id, month, year):
            raise DuplicatePayslipError(employee_id, month, year)

        # Calcul de la paie
        result = self._calc_service.calculate(
            gross_salary=employee.base_salary,
            dependants=employee.dependants_count,
        )

        # Persister le bulletin
        self._payslip_repo.create(
            employee_id=employee.id,
            month=month,
            year=year,
            gross_salary=result.gross_salary,
            cnaps_deduction=result.cnaps_deduction,
            ostie_deduction=result.ostie_deduction,
            fmfp_deduction=result.fmfp_deduction,
            irsa_tax=result.irsa_final,
            net_salary=result.net_salary,
            dependants_count=employee.dependants_count,
        )

        return result

    def generate_batch_payslips(
        self, month: int, year: int
    ) -> list[PayrollResult]:
        """
        Générer les bulletins de paie pour tous les employés actifs.

        Args:
            month: Mois (1-12)
            year: Année

        Returns:
            Liste des résultats de calcul
        """
        self._validate_period(month, year)

        active_employees = self._employee_repo.get_all_active()
        results: list[PayrollResult] = []

        for employee in active_employees:
            # Ignorer si un bulletin existe déjà
            if self._payslip_repo.exists_for_period(employee.id, month, year):
                continue

            try:
                result = self.generate_payslip(employee.id, month, year)
                results.append(result)
            except (EmployeeNotFoundError, DuplicatePayslipError):
                continue

        return results

    def _validate_period(self, month: int, year: int) -> None:
        """Valider la période de paie."""
        if not (1 <= month <= 12):
            raise InvalidPayrollPeriodError(month, year)
        if year < 2000 or year > 2100:
            raise InvalidPayrollPeriodError(month, year)
