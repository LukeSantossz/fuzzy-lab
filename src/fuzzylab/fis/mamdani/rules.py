"""Fuzzy rules for the Mamdani control system (spray, water stress, irrigation)."""

from skfuzzy import control as ctrl

from fuzzylab.fis.mamdani.definitions import (
    bet_productivity,
    delta_t,
    humidity,
    irr_recommendation,
    rain,
    spray_recommendation,
    temperature,
    water_stress,
    wind,
)


def spray_rules():
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
            & (
                wind["calmo"]
                | wind["ideal_pulv"]
                | wind["moderado"]
            ),
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
    Recomendação de irrigação a partir dos termos de `water_stress`
    (encadeamento no mesmo ControlSystem; mínimo duas regras, aqui três).
    """
    return [
        ctrl.Rule(water_stress["baixo"], irr_recommendation["desnecessaria"]),
        ctrl.Rule(water_stress["medio"], irr_recommendation["opcional"]),
        ctrl.Rule(water_stress["alto"], irr_recommendation["recomendada"]),
    ]


def productivity_rules():
    """
    Regras de produtividade estimada (`bp`) baseadas em estresse hídrico
    e condições climáticas. Três cenários: baixa, média e alta produtividade.
    """
    # Alta produtividade: estresse hídrico baixo + condições climáticas favoráveis
    bp_alta_r1 = ctrl.Rule(
        water_stress["baixo"]
        & (temperature["ideal"] | temperature["ameno"])
        & (humidity["ideal"] | humidity["umido"])
        & (rain["leve"] | rain["moderada"]),
        bet_productivity["alta"],
    )

    # Alta produtividade: clima ideal mesmo sem chuva recente (irrigação compensou)
    bp_alta_r2 = ctrl.Rule(
        water_stress["baixo"]
        & temperature["ideal"]
        & humidity["ideal"],
        bet_productivity["alta"],
    )

    # Média produtividade: estresse hídrico médio ou condições parcialmente favoráveis
    bp_medio_r1 = ctrl.Rule(
        water_stress["medio"]
        & (temperature["ameno"] | temperature["ideal"] | temperature["quente"])
        & (humidity["seco"] | humidity["ideal"] | humidity["umido"]),
        bet_productivity["medio"],
    )

    # Média produtividade: baixo estresse mas temperatura subótima
    bp_medio_r2 = ctrl.Rule(
        water_stress["baixo"]
        & (temperature["frio"] | temperature["quente"]),
        bet_productivity["medio"],
    )

    # Baixa produtividade: estresse hídrico alto
    bp_baixa_r1 = ctrl.Rule(
        water_stress["alto"],
        bet_productivity["baixa"],
    )

    # Baixa produtividade: condições climáticas extremas independente do estresse
    bp_baixa_r2 = ctrl.Rule(
        (temperature["frio_extremo"] | temperature["critico"] | temperature["estresse_termico"])
        | (humidity["deserto"] | humidity["condensacao"]),
        bet_productivity["baixa"],
    )

    # Média produtividade: fallback para condições moderadas com chuva relevante
    bp_medio_r3 = ctrl.Rule(
        (rain["moderada"] | rain["forte"])
        & (humidity["umido"] | humidity["saturado"])
        & (temperature["ameno"] | temperature["ideal"] | temperature["frio"]),
        bet_productivity["medio"],
    )

    return [bp_alta_r1, bp_alta_r2, bp_medio_r1, bp_medio_r2, bp_medio_r3, bp_baixa_r1, bp_baixa_r2]


def combined_rules():
    """Cenário de referência para pulverização e produtividade (legado)."""
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


def all_rules():
    return (
        spray_rules()
        + water_stress_rules()
        + irrigation_rules()
        + productivity_rules()
        + combined_rules()
    )


def build_control_system():
    return ctrl.ControlSystem(all_rules())


def build_control_system_simulation():
    return ctrl.ControlSystemSimulation(build_control_system())
