"""
Arquivo de configuração do simulador financeiro.

Aqui ficam todos os parâmetros ajustáveis da simulação:
- renda
- investimento
- fatores macroeconômicos
- parâmetros da simulação Monte Carlo

Separar configurações da lógica principal facilita manutenção,
testes e experimentação de cenários.
"""

# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================

DEBUG = False

ANOS_SIMULACAO = 10
SIMULACOES_MONTE_CARLO = 5000
MONTE_CARLO_LOG_ATIVO = True
MONTE_CARLO_LOG_INTERVALO = 5000

# =========================================================
# CONFIGURAÇÃO FINANCEIRA INICIAL
# =========================================================

CAIXA_INICIAL = 20000
RESERVA_INICIAL = 5000
CAIXA_MINIMO = 2000

# Quando o caixa fica abaixo desse valor, ativa contenção
CAIXA_ALERTA = 10000
FATOR_CONTENCAO_CUSTOS = 0.8

# =========================================================
# PARÂMETROS MACROECONÔMICOS
# =========================================================

CONTRIBUICAO_MEDIA_INICIAL = 300
DESVIO_CONTRIBUICAO = 20

# Crescimento médio anual das contribuições
CRESCIMENTO_CONTRIBUICAO_ANUAL = {
    "pessimista": 0.03,
    "neutro": 0.04,
    "otimista": 0.05
}

# Crescimento médio anual das despesas
CRESCIMENTO_DESPESAS_ANUAL = {
    "pessimista": 0.02,
    "neutro": 0.04,
    "otimista": 0.08
}

# Cenário econômico atual utilizado na simulação
CENARIO_ATUAL = "neutro"

# =========================================================
# COMPORTAMENTO DOS MEMBROS
# =========================================================

MEMBROS_INICIAIS = 85
MEMBROS_LIMITE = 300

# Crescimento natural da comunidade
TAXA_CRESCIMENTO_MEMBROS = 0.35

# Probabilidade de membros deixarem a igreja
PROB_SAIDA_MEMBRO = 0.04

# Intervalo de impacto na saída de membros
SAIDA_MEMBROS_INTERVALO = (0.90, 0.98)

# Fidelidade média de contribuição
TAXA_FIDELIDADE = (0.75, 0.9)

# Peso entre contribuição teórica e contribuição realista
PESO_DIZIMO_BASE = 0.6
PESO_DIZIMO_REALISTA = 0.4

# =========================================================
# EVENTOS IMPREVISÍVEIS
# =========================================================

# Probabilidade de eventos financeiros inesperados
PROB_EVENTO_EXTRA = 0.05

# Intervalo de impacto financeiro desses eventos
VALOR_EVENTO_EXTRA = (300, 2000)

# =========================================================
# CRISE ECONÔMICA
# =========================================================

PROBABILIDADE_CRISE = 0.04

# Impacto da crise nas doações
IMPACTO_DOACAO_CRISE = (0.6, 0.85)

# Impacto da crise no número de membros
IMPACTO_MEMBROS_CRISE = (0.90, 0.98)

# Impacto da crise nos custos
IMPACTO_CUSTOS_CRISE = (1.05, 1.25)

# ==================================
# PARÂMETROS ECONÔMICOS
# ==================================

TAXA_INFLACAO_ANUAL = 0.045
FATOR_RISCO_ECONOMICO = 1.0

# ==================================
# PARÂMETROS DE VOLATILIDADE
# ==================================

FATOR_VOLATILIDADE_BASE = 1.1

# =========================================================
# CATEGORIAS DEPENDENTES DO NÚMERO DE MEMBROS
# =========================================================

CATEGORIAS_DEPENDENTES_MEMBROS = [
    "dizimo",
    "agua",
    "energia",
    "produtos_limpeza"
]

# =========================================================
# CONSTANTES DE MESES
# =========================================================

JANEIRO = 1
FEVEREIRO = 2
MARCO = 3
ABRIL = 4
MAIO = 5
JUNHO = 6
JULHO = 7
AGOSTO = 8
SETEMBRO = 9
OUTUBRO = 10
NOVEMBRO = 11
DEZEMBRO = 12

# =========================================================
# CONFIGURAÇÃO DAS CATEGORIAS FINANCEIRAS
# =========================================================
# media_base: valor médio esperado
# desvio_base: variação natural
# crescimento_anual: crescimento da categoria por cenário
# tipo: entrada ou saída
# aplica_sazonal: se sofre impacto da sazonalidade mensal

CONFIG_VALORES = {
    "dizimo": {
        "media_base": 6000,
        "desvio_base": 2000,
        "crescimento_anual":{
        "pessimista": 0.02,
        "neutro": 0.05,
        "otimista": 0.08,
        },
        "tipo": "entrada",
        "aplica_sazonal": True
    },
    "oferta": {
        "media_base": 1500,
        "desvio_base": 1200,
        "crescimento_anual": {
        "pessimista": 0.01,
        "neutro": 0.02,
        "otimista": 0.03
        },
        "tipo": "entrada",
        "aplica_sazonal": True
    },
    "agua": {
        "media_base": 80,
        "desvio_base": 5,
        "crescimento_anual": {
        "pessimista": 0.02,
        "neutro": 0.03,
        "otimista": 0.04
        },
        "tipo": "saida",
        "aplica_sazonal": False
    },
    "energia": {
        "media_base": 350,
        "desvio_base": 20,
        "crescimento_anual": {
        "pessimista": 0.02,
        "neutro": 0.04,
        "otimista": 0.06
        },
        "tipo": "saida",
        "aplica_sazonal": True
    },
    "produtos_limpeza": {
        "media_base": 450,
        "desvio_base": 30,
        "crescimento_anual": {
        "pessimista": 0.02,
        "neutro": 0.04,
        "otimista": 0.06
        },
        "tipo": "saida",
        "aplica_sazonal": True
    },
    "aluguel": {
        "media_base": 2000,
        "desvio_base": 0,
        "crescimento_anual": {
        "pessimista": 0.03,
        "neutro": 0.06,
        "otimista": 0.08
        },
        "tipo": "saida",
        "aplica_sazonal": False
    },
    "manutencao": {
    "media_base": 500,
    "desvio_base": 400,
    "crescimento_anual": {
        "pessimista": 0.02,
        "neutro": 0.03,
        "otimista": 0.05
    },
    "tipo": "saida",
    "aplica_sazonal": False
    },
    "salario_pastor": {
    "media_base": 3000,
    "desvio_base": 200,
    "crescimento_anual": {
        "pessimista": 0.02,
        "neutro": 0.04,
        "otimista": 0.05
    },
    "tipo": "saida",
    "aplica_sazonal": False
    }
}

# =========================================================
# EVENTOS ESPECIAIS NO ANO
# =========================================================

EVENTOS_ESPECIAIS = {
    3: {
        "nome": "conferencia",
        "entrada_extra": (3000, 8000),
        "custo_extra": (1500, 4000)
    },
    7: {
        "nome": "retiro",
        "entrada_extra": (1000, 3000),
        "custo_extra": (2000, 5000)
    },
    12: {
        "nome": "festa_igreja",
        "entrada_extra": (2000, 7000),
        "custo_extra": (1500, 3500)
    }
}

# =========================================================
# SAZONALIDADE MENSAL
# =========================================================
# Fatores que aumentam ou reduzem entradas e saídas ao longo do ano

SAZONALIDADE = {
    JANEIRO: {"entrada": 0.7, "saida": 1.2},
    FEVEREIRO: {"entrada": 0.8, "saida": 1.1},
    MARCO: {"entrada": 0.9, "saida": 1.0},
    ABRIL: {"entrada": 1.0, "saida": 1.0},
    MAIO: {"entrada": 1.1, "saida": 1.0},
    JUNHO: {"entrada": 1.2, "saida": 1.0},
    JULHO: {"entrada": 1.0, "saida": 1.1},
    AGOSTO: {"entrada": 0.9, "saida": 1.1},
    SETEMBRO: {"entrada": 1.0, "saida": 1.0},
    OUTUBRO: {"entrada": 1.1, "saida": 1.0},
    NOVEMBRO: {"entrada": 1.3, "saida": 1.0},
    DEZEMBRO: {"entrada": 1.5, "saida": 1.2}
}