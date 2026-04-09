"""Antecedents, consequents, and membership functions for the Mamdani FIS."""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

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
