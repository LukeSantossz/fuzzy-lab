"""Mamdani fuzzy inference system for agricultural decision support.

This module consolidates the linguistic variables (antecedents and
consequents), membership functions, rule sets, and the public inference API
for the Mamdani FIS used across the fuzzylab package.

Public interface
----------------
- ``build_system(config)``: build a :class:`ControlSystemSimulation`.
- ``run_inference(system, inputs)``: run inference and return outputs as a
  plain ``dict`` keyed by consequent name (``wh``, ``ir``, ``sp``, ``bp``).

Backward-compatible helpers retained:
- ``build_control_system()`` / ``build_control_system_simulation()``
- ``spray_rules()``, ``water_stress_rules()``, ``irrigation_rules()``,
  ``productivity_rules()``, ``combined_rules()``, ``all_rules()``
"""

from __future__ import annotations

from typing import Callable, Iterable, Mapping

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ---------------------------------------------------------------------------
# Antecedents (inputs)
# ---------------------------------------------------------------------------
temperature = ctrl.Antecedent(np.arange(0, 60, 0.1), "Temperatura")
humidity = ctrl.Antecedent(np.arange(0, 101, 1.0), "Umidade")
rain = ctrl.Antecedent(np.arange(0, 500, 0.2), "Chuva")
wind = ctrl.Antecedent(np.arange(0, 150, 0.5), "Vento")
delta_t = ctrl.Antecedent(np.arange(0, 40, 0.1), "Delta T")

temperature.automf(
    number=7,
    names=[
        "frio_extremo",
        "frio",
        "ameno",
        "ideal",
        "quente",
        "estresse_termico",
        "critico",
    ],
)
humidity.automf(
    number=7,
    names=[
        "deserto",
        "critico_seco",
        "seco",
        "ideal",
        "umido",
        "saturado",
        "condensacao",
    ],
)
rain.automf(
    number=7,
    names=["seco", "trace", "leve", "moderada", "forte", "muito_forte", "extrema"],
)
wind.automf(
    number=7,
    names=[
        "calmo",
        "ideal_pulv",
        "moderado",
        "atencao_pulv",
        "forte",
        "muito_forte",
        "tempestade",
    ],
)
delta_t.automf(
    number=7,
    names=[
        "inversao_termica",
        "ideal_pulv",
        "aceitavel",
        "atencao",
        "critico_pulv",
        "proibido",
        "extremo",
    ],
)

# ---------------------------------------------------------------------------
# Consequents (outputs)
# ---------------------------------------------------------------------------
spray_recommendation = ctrl.Consequent(np.arange(0, 11, 1), "sp")
spray_recommendation["proibida"] = fuzz.trimf(spray_recommendation.universe, [0, 0, 4])
spray_recommendation["atencao"] = fuzz.trimf(spray_recommendation.universe, [3, 5, 7])
spray_recommendation["janela_disponivel"] = fuzz.trimf(
    spray_recommendation.universe, [6, 10, 10]
)

water_stress = ctrl.Consequent(np.arange(0, 1.1, 0.1), "wh")
water_stress["baixo"] = fuzz.trimf(water_stress.universe, [0, 0.2, 1])
water_stress["medio"] = fuzz.trimf(water_stress.universe, [0, 0.5, 1])
water_stress["alto"] = fuzz.trimf(water_stress.universe, [0.5, 0.8, 1])

irr_recommendation = ctrl.Consequent(np.arange(0, 11, 1), "ir")
irr_recommendation["desnecessaria"] = fuzz.trimf(irr_recommendation.universe, [0, 3, 4])
irr_recommendation["opcional"] = fuzz.trimf(irr_recommendation.universe, [0, 5, 6])
irr_recommendation["recomendada"] = fuzz.trimf(irr_recommendation.universe, [5, 9, 10])

bet_productivity = ctrl.Consequent(np.arange(0, 101, 1), "bp")
bet_productivity["baixa"] = fuzz.trimf(bet_productivity.universe, [0, 10, 40])
bet_productivity["medio"] = fuzz.trimf(bet_productivity.universe, [0, 50, 70])
bet_productivity["alta"] = fuzz.trimf(bet_productivity.universe, [50, 80, 100])


# ---------------------------------------------------------------------------
# Rule sets
# ---------------------------------------------------------------------------
def spray_rules() -> list[ctrl.Rule]:
    """Recomendação de pulverização."""
    return [
        ctrl.Rule(
            delta_t["ideal_pulv"]
            & (rain["seco"] | rain["trace"])
            & humidity["ideal"]
            & temperature["ideal"],
            spray_recommendation["janela_disponivel"],
        ),
        ctrl.Rule(
            (delta_t["aceitavel"] | delta_t["atencao"])
            & rain["trace"]
            & (humidity["seco"] | humidity["umido"])
            & (temperature["ameno"] | temperature["quente"]),
            spray_recommendation["atencao"],
        ),
        ctrl.Rule(
            wind["atencao_pulv"]
            & (rain["seco"] | rain["trace"])
            & humidity["ideal"]
            & temperature["ideal"],
            spray_recommendation["atencao"],
        ),
        ctrl.Rule(
            rain["leve"]
            & (delta_t["ideal_pulv"] | delta_t["aceitavel"])
            & (wind["calmo"] | wind["ideal_pulv"] | wind["moderado"]),
            spray_recommendation["atencao"],
        ),
        ctrl.Rule(
            temperature["frio"]
            & (delta_t["ideal_pulv"] | delta_t["aceitavel"])
            & (rain["seco"] | rain["trace"]),
            spray_recommendation["atencao"],
        ),
        ctrl.Rule(
            humidity["deserto"] | humidity["critico_seco"],
            spray_recommendation["atencao"],
        ),
        ctrl.Rule(
            (delta_t["critico_pulv"] | delta_t["proibido"])
            & (
                rain["forte"]
                | rain["muito_forte"]
                | rain["extrema"]
                | rain["moderada"]
            ),
            spray_recommendation["proibida"],
        ),
        ctrl.Rule(
            delta_t["inversao_termica"] | delta_t["extremo"],
            spray_recommendation["proibida"],
        ),
        ctrl.Rule(
            wind["tempestade"] | wind["forte"] | wind["muito_forte"],
            spray_recommendation["proibida"],
        ),
        ctrl.Rule(
            temperature["frio_extremo"]
            | temperature["critico"]
            | temperature["estresse_termico"],
            spray_recommendation["proibida"],
        ),
        ctrl.Rule(
            humidity["saturado"] | humidity["condensacao"],
            spray_recommendation["proibida"],
        ),
    ]


def water_stress_rules() -> list[ctrl.Rule]:
    """Regras de estresse hídrico (3 centrais + 3 extensões de fronteira).

    Há três regras centrais (baixo, médio, alto) e extensões para fronteiras
    do universo onde, sem elas, o skfuzzy não agrega saída para ``wh``.
    """
    umidade_confortavel = (
        humidity["ideal"]
        | humidity["umido"]
        | humidity["saturado"]
        | humidity["condensacao"]
    )
    chuva_que_alivia = (
        rain["trace"]
        | rain["leve"]
        | rain["moderada"]
        | rain["forte"]
        | rain["muito_forte"]
        | rain["extrema"]
    )
    wh_baixo = ctrl.Rule(
        umidade_confortavel & chuva_que_alivia,
        water_stress["baixo"],
    )

    wh_medio = ctrl.Rule(
        (humidity["seco"] | humidity["ideal"])
        & (rain["trace"] | rain["leve"])
        & (temperature["ameno"] | temperature["ideal"]),
        water_stress["medio"],
    )

    solo_arido = humidity["deserto"] | humidity["critico_seco"]
    pouca_chuva = rain["seco"] | rain["trace"]
    calor_estresse = (
        temperature["quente"]
        | temperature["estresse_termico"]
        | temperature["critico"]
    )
    wh_alto = ctrl.Rule(
        solo_arido & pouca_chuva & calor_estresse,
        water_stress["alto"],
    )

    ar_umido_sem_chuva = ctrl.Rule(
        (humidity["umido"] | humidity["saturado"] | humidity["condensacao"])
        & (rain["seco"] | rain["trace"]),
        water_stress["baixo"],
    )
    seco_sem_calor = ctrl.Rule(
        solo_arido
        & pouca_chuva
        & (
            temperature["frio"]
            | temperature["frio_extremo"]
            | temperature["ameno"]
            | temperature["ideal"]
        ),
        water_stress["medio"],
    )
    ar_seco_chuva_relevante = ctrl.Rule(
        (humidity["deserto"] | humidity["critico_seco"] | humidity["seco"])
        & (
            rain["leve"]
            | rain["moderada"]
            | rain["forte"]
            | rain["muito_forte"]
            | rain["extrema"]
        ),
        water_stress["medio"],
    )

    return [
        wh_baixo,
        wh_medio,
        wh_alto,
        ar_umido_sem_chuva,
        seco_sem_calor,
        ar_seco_chuva_relevante,
    ]


def irrigation_rules() -> list[ctrl.Rule]:
    """Recomendação de irrigação encadeada a partir de ``water_stress``."""
    return [
        ctrl.Rule(water_stress["baixo"], irr_recommendation["desnecessaria"]),
        ctrl.Rule(water_stress["medio"], irr_recommendation["opcional"]),
        ctrl.Rule(water_stress["alto"], irr_recommendation["recomendada"]),
    ]


def productivity_rules() -> list[ctrl.Rule]:
    """Regras de produtividade estimada (``bp``)."""
    bp_alta_r1 = ctrl.Rule(
        water_stress["baixo"]
        & (temperature["ideal"] | temperature["ameno"])
        & (humidity["ideal"] | humidity["umido"])
        & (rain["leve"] | rain["moderada"]),
        bet_productivity["alta"],
    )
    bp_alta_r2 = ctrl.Rule(
        water_stress["baixo"] & temperature["ideal"] & humidity["ideal"],
        bet_productivity["alta"],
    )
    bp_medio_r1 = ctrl.Rule(
        water_stress["medio"]
        & (temperature["ameno"] | temperature["ideal"] | temperature["quente"])
        & (humidity["seco"] | humidity["ideal"] | humidity["umido"]),
        bet_productivity["medio"],
    )
    bp_medio_r2 = ctrl.Rule(
        water_stress["baixo"] & (temperature["frio"] | temperature["quente"]),
        bet_productivity["medio"],
    )
    bp_baixa_r1 = ctrl.Rule(
        water_stress["alto"],
        bet_productivity["baixa"],
    )
    bp_baixa_r2 = ctrl.Rule(
        (
            temperature["frio_extremo"]
            | temperature["critico"]
            | temperature["estresse_termico"]
        )
        | (humidity["deserto"] | humidity["condensacao"]),
        bet_productivity["baixa"],
    )
    bp_medio_r3 = ctrl.Rule(
        (rain["moderada"] | rain["forte"])
        & (humidity["umido"] | humidity["saturado"])
        & (temperature["ameno"] | temperature["ideal"] | temperature["frio"]),
        bet_productivity["medio"],
    )
    return [
        bp_alta_r1,
        bp_alta_r2,
        bp_medio_r1,
        bp_medio_r2,
        bp_medio_r3,
        bp_baixa_r1,
        bp_baixa_r2,
    ]


def combined_rules() -> list[ctrl.Rule]:
    """Cenário de referência legado (pulverização + produtividade)."""
    return [
        ctrl.Rule(
            temperature["ideal"]
            & humidity["ideal"]
            & rain["moderada"]
            & wind["moderado"]
            & delta_t["aceitavel"],
            (
                spray_recommendation["janela_disponivel"],
                bet_productivity["medio"],
            ),
        )
    ]


_RULE_REGISTRY: dict[str, Callable[[], list[ctrl.Rule]]] = {
    "spray": spray_rules,
    "water_stress": water_stress_rules,
    "irrigation": irrigation_rules,
    "productivity": productivity_rules,
    "combined": combined_rules,
}

DEFAULT_RULE_GROUPS: tuple[str, ...] = (
    "spray",
    "water_stress",
    "irrigation",
    "productivity",
    "combined",
)


def all_rules() -> list[ctrl.Rule]:
    """Return the default union of every rule group."""
    return _collect_rules(DEFAULT_RULE_GROUPS)


def _collect_rules(groups: Iterable[str]) -> list[ctrl.Rule]:
    rules: list[ctrl.Rule] = []
    for name in groups:
        try:
            builder = _RULE_REGISTRY[name]
        except KeyError as exc:
            raise ValueError(
                f"Unknown rule group {name!r}; "
                f"expected one of {sorted(_RULE_REGISTRY)}"
            ) from exc
        rules.extend(builder())
    return rules


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------
def build_system(config: Mapping[str, object] | None = None) -> ctrl.ControlSystemSimulation:
    """Build and return a Mamdani ``ControlSystemSimulation``.

    Parameters
    ----------
    config : mapping, optional
        Optional configuration. Supported keys:

        - ``"rule_groups"``: iterable of rule-group names to include. Valid
          names are ``"spray"``, ``"water_stress"``, ``"irrigation"``,
          ``"productivity"``, ``"combined"``. Defaults to all groups.

    Returns
    -------
    skfuzzy.control.ControlSystemSimulation
        A simulation instance ready to receive inputs via
        :func:`run_inference`.
    """
    cfg = dict(config) if config else {}
    groups = cfg.get("rule_groups", DEFAULT_RULE_GROUPS)
    rules = _collect_rules(groups)
    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


def run_inference(
    system: ctrl.ControlSystemSimulation,
    inputs: Mapping[str, float],
) -> dict[str, float]:
    """Run inference on ``system`` with ``inputs`` and return the outputs.

    Parameters
    ----------
    system : skfuzzy.control.ControlSystemSimulation
        Simulation built by :func:`build_system`.
    inputs : mapping
        Mapping of antecedent name (``"Temperatura"``, ``"Umidade"``,
        ``"Chuva"``, ``"Vento"``, ``"Delta T"``) to numeric values.

    Returns
    -------
    dict[str, float]
        Crisp defuzzified outputs keyed by consequent name (``wh``, ``ir``,
        ``sp``, ``bp``).
    """
    for key, value in inputs.items():
        system.input[key] = value
    system.compute()
    return {key: float(value) for key, value in system.output.items()}


# ---------------------------------------------------------------------------
# Backward-compatible helpers
# ---------------------------------------------------------------------------
def build_control_system() -> ctrl.ControlSystem:
    return ctrl.ControlSystem(all_rules())


def build_control_system_simulation() -> ctrl.ControlSystemSimulation:
    return ctrl.ControlSystemSimulation(build_control_system())


__all__ = [
    # public interface
    "build_system",
    "run_inference",
    # linguistic variables
    "temperature",
    "humidity",
    "rain",
    "wind",
    "delta_t",
    "spray_recommendation",
    "water_stress",
    "irr_recommendation",
    "bet_productivity",
    # rule builders
    "spray_rules",
    "water_stress_rules",
    "irrigation_rules",
    "productivity_rules",
    "combined_rules",
    "all_rules",
    # backward-compat
    "build_control_system",
    "build_control_system_simulation",
]
