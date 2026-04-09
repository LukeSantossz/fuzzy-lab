"""Fuzzy rules for the Mamdani control system (spray, water stress, irrigation)."""

from skfuzzy import control as ctrl

from fuzzylab.fis.mamdani.definitions import (
    bet_productivity,
    delta_t,
    humidity,
    irr_recomendation,
    rain,
    spray_recomendation,
    temperature,
    water_stress,
    wind,
)


def spray_rules():
    """Task 3 — recomendação de pulverização."""
    return [
        ctrl.Rule(
            delta_t["ideal_pulv"]
            & (rain["seco"] | rain["trace"])
            & humidity["ideal"]
            & temperature["ideal"],
            spray_recomendation["janela_disponivel"],
        ),
        ctrl.Rule(
            (delta_t["aceitavel"] | delta_t["atencao"])
            & rain["trace"]
            & (humidity["seco"] | humidity["umido"])
            & (temperature["ameno"] | temperature["quente"]),
            spray_recomendation["atencao"],
        ),
        ctrl.Rule(
            wind["atencao_pulv"]
            & (rain["seco"] | rain["trace"])
            & humidity["ideal"]
            & temperature["ideal"],
            spray_recomendation["atencao"],
        ),
        ctrl.Rule(
            rain["leve"]
            & (delta_t["ideal_pulv"] | delta_t["aceitavel"])
            & (
                wind["calmo"]
                | wind["ideal_pulv"]
                | wind["moderado"]
            ),
            spray_recomendation["atencao"],
        ),
        ctrl.Rule(
            temperature["frio"]
            & (delta_t["ideal_pulv"] | delta_t["aceitavel"])
            & (rain["seco"] | rain["trace"]),
            spray_recomendation["atencao"],
        ),
        ctrl.Rule(
            humidity["deserto"] | humidity["critico_seco"],
            spray_recomendation["atencao"],
        ),
        ctrl.Rule(
            (delta_t["critico_pulv"] | delta_t["proibido"])
            & (
                rain["forte"]
                | rain["muito_forte"]
                | rain["extrema"]
                | rain["moderada"]
            ),
            spray_recomendation["proibida"],
        ),
        ctrl.Rule(
            delta_t["inversao_termica"] | delta_t["extremo"],
            spray_recomendation["proibida"],
        ),
        ctrl.Rule(
            wind["tempestade"] | wind["forte"] | wind["muito_forte"],
            spray_recomendation["proibida"],
        ),
        ctrl.Rule(
            temperature["frio_extremo"]
            | temperature["critico"]
            | temperature["estresse_termico"],
            spray_recomendation["proibida"],
        ),
        ctrl.Rule(
            humidity["saturado"] | humidity["condensacao"],
            spray_recomendation["proibida"],
        ),
    ]


def water_stress_rules():
    """
    Há três regras centrais (baixo, médio, alto) e extensões para fronteiras
    do universo onde, sem elas, o skfuzzy não agrega saída para `wh`.
    """
    umidade_confortavel = (
        humidity["ideal"]
        | humidity["umido"]
        | humidity["saturado"]
        | humidity["condensacao"]
    )
    # Inclui trace/leve: volumes moderados no universo 0–500 mm ativam sobretudo "leve".
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

    # Extremos de fronteira: garante ativação de `wh` (e encadeamento `ir`) no skfuzzy.
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


def irrigation_rules():
    """
    Task 4 — recomendação de irrigação a partir dos termos de `water_stress`
    (encadeamento no mesmo ControlSystem; mínimo duas regras, aqui três).
    """
    return [
        ctrl.Rule(water_stress["baixo"], irr_recomendation["desnecessaria"]),
        ctrl.Rule(water_stress["medio"], irr_recomendation["opcional"]),
        ctrl.Rule(water_stress["alto"], irr_recomendation["recomendada"]),
    ]


def combined_rules():
    """Cenário de referência para pulverização e produtividade (Task 5)."""
    return [
        ctrl.Rule(
            temperature["ideal"]
            & humidity["ideal"]
            & rain["moderada"]
            & wind["moderado"]
            & delta_t["aceitavel"],
            (
                spray_recomendation["janela_disponivel"],
                bet_productivity["medio"],
            ),
        )
    ]


def all_rules():
    return (
        spray_rules()
        + water_stress_rules()
        + irrigation_rules()
        + combined_rules()
    )


def build_control_system():
    return ctrl.ControlSystem(all_rules())


def build_control_system_simulation():
    return ctrl.ControlSystemSimulation(build_control_system())
