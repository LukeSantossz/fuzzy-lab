"""Boundary and integration checks for water stress and irrigation rules."""

import pytest

from fuzzylab.fis.mamdani.rules import build_control_system_simulation


def _simulate(*, temperatura, umidade, chuva, vento, delta_t):
    sim = build_control_system_simulation()
    sim.input["Temperatura"] = temperatura
    sim.input["Umidade"] = umidade
    sim.input["Chuva"] = chuva
    sim.input["Vento"] = vento
    sim.input["Delta T"] = delta_t
    sim.compute()
    return sim


def test_outputs_include_wh_and_ir_after_compute():
    sim = _simulate(
        temperatura=28.0,
        umidade=60.0,
        chuva=0.0,
        vento=10.0,
        delta_t=8.0,
    )
    assert "wh" in sim.output
    assert "ir" in sim.output
    assert 0.0 <= float(sim.output["wh"]) <= 1.0
    assert 0.0 <= float(sim.output["ir"]) <= 10.0


@pytest.mark.parametrize(
    "umidade,chuva,expect_wh_low",
    [
        (0.0, 0.0, False),
        (100.0, 0.0, False),
        (0.0, 100.0, False),
        (100.0, 400.0, True),
    ],
)
def test_boundary_inputs_produce_crisp_outputs(umidade, chuva, expect_wh_low):
    """Extremos 0/100 (umidade) e chuva nos limites não devem quebrar a simulação."""
    sim = _simulate(
        temperatura=25.0,
        umidade=float(umidade),
        chuva=float(chuva),
        vento=5.0,
        delta_t=10.0,
    )
    assert "wh" in sim.output
    wh = float(sim.output["wh"])
    assert 0.0 <= wh <= 1.0
    if expect_wh_low:
        assert wh <= 0.51


def test_three_scenarios_ordering_seco_worse_than_chuvoso():
    seco = _simulate(
        temperatura=38.0,
        umidade=12.0,
        chuva=0.0,
        vento=10.0,
        delta_t=8.0,
    )
    normal = _simulate(
        temperatura=26.0,
        umidade=55.0,
        chuva=8.0,
        vento=12.0,
        delta_t=8.0,
    )
    chuvoso = _simulate(
        temperatura=22.0,
        umidade=88.0,
        chuva=150.0,
        vento=15.0,
        delta_t=7.0,
    )
    wh_seco = float(seco.output["wh"])
    wh_normal = float(normal.output["wh"])
    wh_chuvoso = float(chuvoso.output["wh"])
    ir_seco = float(seco.output["ir"])
    ir_chuvoso = float(chuvoso.output["ir"])

    assert wh_seco > wh_normal > wh_chuvoso
    assert ir_seco > ir_chuvoso


def test_productivity_output_exists_and_in_range():
    """Verifica que bp está presente e dentro do universo 0-100."""
    sim = _simulate(
        temperatura=26.0,
        umidade=60.0,
        chuva=20.0,
        vento=10.0,
        delta_t=8.0,
    )
    assert "bp" in sim.output
    bp = float(sim.output["bp"])
    assert 0.0 <= bp <= 100.0


def test_productivity_inversely_correlated_with_water_stress():
    """Cenário seco (alto wh) deve ter menor produtividade que cenário úmido (baixo wh)."""
    # Cenário seco: alta temperatura, baixa umidade, sem chuva
    seco = _simulate(
        temperatura=38.0,
        umidade=10.0,
        chuva=0.0,
        vento=8.0,
        delta_t=8.0,
    )
    # Cenário favorável: temperatura ideal, umidade ideal, chuva moderada (150mm em universo 0-500)
    favoravel = _simulate(
        temperatura=25.0,
        umidade=55.0,
        chuva=150.0,
        vento=8.0,
        delta_t=6.0,
    )
    bp_seco = float(seco.output["bp"])
    bp_favoravel = float(favoravel.output["bp"])
    wh_seco = float(seco.output["wh"])
    wh_favoravel = float(favoravel.output["wh"])

    assert wh_seco > wh_favoravel, "Cenário seco deve ter maior estresse hídrico"
    assert bp_seco < bp_favoravel, "Cenário seco deve ter menor produtividade"
