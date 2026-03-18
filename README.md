# Fuzzy Lab

Sistema de suporte à decisão agrícola que utiliza lógica fuzzy com regras do tipo **SE-ENTÃO** para recomendar janelas de pulverização, monitorar estresse hídrico, sugerir irrigação e estimar produtividade, com base em variáveis climáticas.

## O que é?

Um pacote modular em Python que implementa **Sistemas de Inferência Fuzzy (FIS)**, **ANFIS** e análise de **séries temporais** para agricultura de precisão.

## Estrutura do projeto

```
fuzzy-lab/
├── src/fuzzylab/           # Pacote principal
│   ├── fis/                # FIS Mamdani
│   ├── anfis/              # Redes neuro-fuzzy adaptativas
│   └── timeseries/         # Análise de séries temporais
├── notebooks/              # Notebooks de experimentação
├── data/raw/               # Dados brutos
├── tests/                  # Testes unitários
└── requirements-*.txt      # Dependências por módulo
```

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python | Linguagem principal |
| [scikit-fuzzy](https://pythonhosted.org/scikit-fuzzy/) | Motor de inferência fuzzy (Mamdani) |
| NumPy | Manipulação de universos de discurso |
| PyTorch | Redes neuro-fuzzy (ANFIS) |
| tslearn / Pandas | Análise de séries temporais |
| pytest | Testes unitários |
| Jupyter Notebook | Ambiente de experimentação |

## Variáveis

**Antecedentes (entradas):**
- `Temperatura` — 0 a 60 °C (7 conjuntos: frio_extremo → crítico)
- `Umidade` — 0 a 100 % (7 conjuntos: deserto → condensação)
- `Chuva` — 0 a 500 mm (7 conjuntos: seco → extrema)
- `Vento` — 0 a 150 km/h (7 conjuntos: calmo → tempestade)
- `Delta T` — 0 a 40 °C (7 conjuntos: inversão_térmica → extremo)

**Consequentes (saídas):**
- `Recomendação de Pulverização` — proibida / atenção / janela_disponível
- `Estresse Hídrico`
- `Recomendação de Irrigação`
- `Produtividade Estimada`

## Instalação

```bash
# FIS Mamdani
pip install -r requirements-fis.txt

# ANFIS (redes neuro-fuzzy)
pip install -r requirements-anfis.txt

# Séries temporais
pip install -r requirements-timeseries.txt

# Desenvolvimento (testes, notebooks)
pip install -r requirements-dev.txt
```

## Estágio do projeto

**Em andamento.** Estrutura modular criada com FIS Mamdani funcional para recomendação de pulverização.

- [x] Definição dos antecedentes e consequentes
- [x] Funções de pertinência (automf com 7 conjuntos)
- [x] Regras completas de pulverização (`janela_disponivel`, `atencao`, `proibida`)
- [x] Estrutura modular do pacote (`fis`, `anfis`, `timeseries`)
- [ ] Regras para estresse hídrico, irrigação e produtividade
- [ ] Implementação do módulo ANFIS
- [ ] Implementação do módulo de séries temporais
- [ ] Validação dos intervalos com literatura técnica e climatologia regional

## Problemas conhecidos

- Os intervalos dos universos de discurso (`np.arange`) precisam ser confirmados com base na climatologia registrada da região e literatura técnica agronômica.
- Os intervalos para `bet_productivity` precisam de revisão criteriosa com literatura técnica.
- Módulos ANFIS e timeseries ainda não implementados (apenas estrutura de diretórios).
