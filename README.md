# Finance Analytics Pipeline — V2

![Python](https://img.shields.io/badge/python-3.14+-blue)
![Pandas](https://img.shields.io/badge/pandas-data%20analysis-orange)
![Monte Carlo](https://img.shields.io/badge/simulation-monte%20carlo-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Simulador financeiro desenvolvido em Python para gerar cenários econômicos, simular fluxo de caixa e aplicar **simulação de Monte Carlo** para avaliação de risco financeiro.

O projeto gera dados simulados de receitas, custos e caixa ao longo do tempo e permite explorar os resultados por meio de **análise exploratória em Jupyter Notebook**.

> **Versão atual: 2.1.0 (03/09/2026).** Esta versão marca a evolução do motor para Programação Orientada a Objetos, testes automatizados e logging centralizado. O histórico técnico completo está em [CHANGELOG.md](CHANGELOG.md).

---

## Contexto do projeto

A ideia deste projeto surgiu a partir de uma experiência prática na gestão financeira de uma organização comunitária, onde atuo como tesoureira.

Durante essa experiência, percebi a dificuldade de analisar cenários financeiros futuros apenas com base em registros históricos simples de entradas e saídas. Isso motivou a criação de um simulador capaz de gerar cenários econômicos e ajudar na análise de sustentabilidade financeira ao longo do tempo.

Inicialmente o projeto foi pensado apenas como um **gerador de dados simulados de fluxo de caixa**, mas evoluiu para algo mais completo: um **simulador financeiro com análise probabilística**, capaz de apoiar a tomada de decisões através de técnicas como **simulação de Monte Carlo**.

O objetivo é explorar perguntas como:

- Qual o risco de uma organização ficar sem caixa no futuro?
- Como variações econômicas podem afetar receitas e despesas?
- Qual o impacto de crescimento ou redução de contribuições ao longo do tempo?

A partir dessas simulações, é possível gerar métricas financeiras e visualizar cenários que ajudam na compreensão do risco e da sustentabilidade do sistema financeiro analisado.

---

## Objetivo

Este projeto tem como objetivo demonstrar técnicas utilizadas em **análise de dados financeiros**, incluindo:

- Simulação de fluxo de caixa
- Modelagem de cenários econômicos
- Simulação de Monte Carlo
- Geração automática de datasets
- Análise exploratória de dados
- Visualização de resultados

---

## Arquitetura do simulador

O projeto foi estruturado com separação clara de responsabilidades para facilitar manutenção, evolução e adaptação do modelo.

A lógica do sistema está dividida em três componentes principais:

- **`conf.py`**
    Arquivo responsável pelas **configurações e parâmetros do modelo**, incluindo taxas econômicas, probablidades, limites financeiros e cenários. Isso permite ajustar o comportamento da simulação sem modificar o motor do sistema.
- **`simulation_engine.py`**
    Contém o **motor da simulação**, onde são implementadas as regras de negócio, geração de transações, eventos econômicos, cálculo de métricas e execução das simulações Monte Carlo.
- **`main.py`**
    Responsável pela **execução do pipeline**, chamando a simulação, gerando os datasets e exibindo os resultados.

Essa separação permite que o modelo seja facilmente adaptado para diferentes cenários financeiros apenas modificando parâmetros no arquivo de configuração (`conf.py`).

## Evolução arquitetural — V2

A primeira versão separava configuração, motor e execução, mas o motor concentrava regras em funções globais e representava o estado com dicionários. Isso dificultava localizar responsabilidades, testar regras isoladas e evoluir o domínio sem aumentar o acoplamento.

Na V2, os elementos do negócio passaram a ter representação explícita:

| Componente | Responsabilidade |
| --- | --- |
| `EstadoFinanceiro` | Mantém caixa, reserva, membros e histórico; aplica transações e usa a reserva quando necessário. |
| `EstadoEconomico` | Representa inflação, crise e seus impactos no período. |
| `Transacao` e `RegistroMensal` | Modelam movimentações e resultados mensais com tipos próprios. |
| `SimuladorFinanceiro` | Executa regras de negócio e produz um `ResultadoSimulacao`. |
| `AnaliseMonteCarlo` | Executa cenários repetidos e calcula indicadores de risco. |
| `GeradorGraficos` | Gera os gráficos sem misturar visualização com regras financeiras. |

Essa mudança preserva a interface de execução e os arquivos de saída da V1, mas deixa o projeto mais testável, previsível e preparado para novas regras. A utilização da reserva, antes existente como função isolada, também passou a integrar o fluxo real da simulação.

### Rastreabilidade da evolução

- **V1:** funções e dicionários, com separação inicial entre configuração, motor e execução.
- **V2:** domínio modelado por classes, responsabilidades isoladas, gerador aleatório injetável para reprodutibilidade e cobertura automatizada de regras críticas.
- Cada mudança relevante deve ser registrada em [CHANGELOG.md](CHANGELOG.md), preservando a história técnica do projeto.

---

## Tecnologias utilizadas

- Python
- Pandas
- Matplotlib
- Jupyter Notebook

## Estrutura do projeto

```bash

finance-analytics-pipeline
│
├── analysis
│   └── exploracao_simulacoes.ipynb
│
├── data
│   ├── 01_simulacao.csv
│   └── 02_montecarlo.csv
│
├── docs
│   ├── distribuicao_caixa.png
│   ├── evolucao_caixa.png
│   └── projecao_probabilistica.png
│
├── conf.py
├── simulation_engine.py
├── main.py
├── tests
│   └── test_simulation_engine.py
│
├── CHANGELOG.md
├── requirements.txt
└── README.md
```

---

## Instalação

Clone o repositório:

```bash
git clone https://github.com/marinizedeev/finance-analytics-pipeline.git
cd finance-analytics-pipeline
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Como executar

Execute o simulador principal:

```bash
python main.py
```

O sistema irá:

1. Rodar a simulação financeira
2. Executar múltiplas simulações de Monte Carlo
3. Gerar arquivos CSV na pasta `data`
4. Exibir gráficos de análise

## Testes automatizados

A V2 utiliza a biblioteca padrão `unittest`, portanto não exige dependências adicionais. Para executar toda a suíte:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem regras essenciais do domínio: atualização de caixa por tipo de transação, uso de reserva, contenção de custos, eventos planejados, estrutura dos resultados, reprodutibilidade com semente aleatória e resultados da análise Monte Carlo.

## Logs

As mensagens do pipeline utilizam o módulo padrão `logging` — não há mensagens de execução com `print`. Os logs são emitidos no terminal e salvos em `logs/finance_pipeline.log`, com rotação automática de arquivo para limitar o uso de disco.

O nível e a retenção são configuráveis em `conf.py`:

- `LOG_NIVEL`: nível mínimo registrado, como `INFO` ou `DEBUG`.
- `LOG_ARQUIVO`: caminho do arquivo de log.
- `LOG_MAX_BYTES` e `LOG_BACKUP_COUNT`: tamanho máximo e quantidade de arquivos rotacionados.

O arquivo de log é ignorado pelo Git; assim, o repositório mantém a configuração versionada sem incluir saídas locais de execução.

---

## Análise de dados

Após gerar os dados, abra o notebook:

```bash
analysis/exploracao_simulacoes.ipynb
```

No notebook é possível:

- Carregar os datasets gerados
- Analisar estatísticas
- Visualizar distribuições
- Explorar cenários financeiros

---

## Exemplos de análise

Algumas análises possíveis com os dados gerados:

- Evolução do caixa ao longo do tempo
- Distribuição de resultados da simulação Monte Carlo
- Análise de risco financeiro
- Comparação entre cenários

---

## Exemplos de resultados

![Distribuição do Caixa](docs/distribuicao_caixa.png)

![Evolução do Caixa](docs/evolucao_caixa.png)

![Projeção Probabilística do Caixa](docs/projecao_probabilistica.png)

---

## Possíveis melhorias futuras

- Criar objetos de configuração para substituir as constantes globais de `conf.py`
- Adicionar mais variáveis econômicas e cenários macroeconômicos
- Criar dashboard interativo
- Automatizar geração de relatórios
- Adicionar integração contínua para executar os testes a cada alteração

## Autora

Marinize Santana → estudante de Análise e Desenvolvimento de Sistemas.

Projeto desenvolvido como prática de **engenharia de dados e análise financeira com Python**.
