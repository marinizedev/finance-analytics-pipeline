# Imports
import random
from conf import *
import pandas as pd
import matplotlib.pyplot as plt


# Estado Inicial
def iniciar_estado():
    """
    Inicializa o estado financeiro da simulação.
    """
    return {
        "caixa": CAIXA_INICIAL,
        "reserva": RESERVA_INICIAL,
        "membros": MEMBROS_INICIAIS,
        "historico": []
    }

def iniciar_estado_simulacao():
    """
    Inicializa estado macroeconômico da simulação.
    """
    return {
        "duracao_crise": 0,
        "duracao_crise_total": 0,
        "impacto_doacao": 1.0,
        "impacto_membros": 1.0,
        "impacto_custos": 1.0,
        "inflacao_anual": TAXA_INFLACAO_ANUAL
    }


# Modelos Econômicos
def crise_global():
    """
    Simula uma crise econômica global que pode impactar a organização.
    """
    if random.random() < PROBABILIDADE_CRISE:
        duracao = random.randint(3, 12)

        impacto_doacao = random.uniform(*IMPACTO_DOACAO_CRISE)
        impacto_membros = random.uniform(*IMPACTO_MEMBROS_CRISE)
        impacto_custos = random.uniform(*IMPACTO_CUSTOS_CRISE)
        return  duracao, impacto_doacao, impacto_membros, impacto_custos
    return 0, 1.0, 1.0, 1.0

def fator_economico():
    """
    Gera um fator macroeconômico aleatório que afeta receitas e despesas.
    Representa pequenas oscilações na economia (±5%).
    """
    return random.normalvariate(1, 0.05)

def crise_economica():
    """
    Representa crises econômicas pontuais que afetam temporariamente
    as receitas da organização.
    """
    if random.random() < 0.08: 
        return random.uniform(0.6, 0.85) 
    return 1

def queda_doacoes():
    """
    Simula períodos de queda nas doações da comunidade.
    Pode representar crises pessoais ou redução de participação.
    """
    if random.random() < 0.05:
        return random.uniform(0.8, 0.95)
    return 1

def aplicar_risco_economico(valor):
    """
    Aplica fator macroeconômico no valor da transação.
    """
    return valor * FATOR_RISCO_ECONOMICO

def fator_inflacao(ano, mes, inflacao_anual):
    """
    Calcula inflação composta mensal acumulada.
    """
    inflacao_mensal = (1 + inflacao_anual) ** (1/12) - 1
    meses_passados = ano * 12 + (mes - 1)
    return (1 + inflacao_mensal) ** meses_passados

def inflacao_ano():
    """
    Gera inflação anual variável.
    """
    inflacao = random.normalvariate(TAXA_INFLACAO_ANUAL, 0.01)
    return max(-0.02, inflacao)

def usar_reserva(estado):
    """
    Usa reserva financeira caso o caixa fique abaixo do mínimo.
    """
    if estado["caixa"] < CAIXA_MINIMO and estado["reserva"] > 0:

        necessario = CAIXA_MINIMO - estado["caixa"]
        saque = min(necessario, estado["reserva"])

        estado["reserva"] -= saque
        estado["caixa"] += saque

    return estado


# Modelo da Igreja (membros/dízimo)
def calcular_membros(ano, impacto_membros):
    """
    Calcula o número estimado de membros da organização ao longo do tempo.
    """
    base = MEMBROS_INICIAIS
    limite = MEMBROS_LIMITE
    k = TAXA_CRESCIMENTO_MEMBROS
    membros = limite / (1 + ((limite - base) / base) * (2.718 ** (-k * ano)))
    perda = perda_membros()
    return membros * impacto_membros * perda

def calcular_contribuicao_media(ano):
    """
    Calcula a contribuição média por membro para o período atual.
    """
    crescimento = CRESCIMENTO_CONTRIBUICAO_ANUAL[CENARIO_ATUAL]
    media = CONTRIBUICAO_MEDIA_INICIAL * ((1 + crescimento) ** ano)
    contribuicao = random.normalvariate(media, DESVIO_CONTRIBUICAO)
    return max(contribuicao, 0)

def calcular_dizimo(ano, impacto_membros):
    """
    Calcula o valor total estimado de dízimos para o período.
    """
    membros = calcular_membros(ano, impacto_membros)
    contribuicao_media = calcular_contribuicao_media(ano)
    dizimo = membros * contribuicao_media
    return dizimo

def calcular_dizimo_realista(ano, membros_mes, impacto_doacao):
    """
    Calcula uma estimativa alternativa de dízimos baseada em
    comportamento realista dos membros.
    """
    contribuicao_media = calcular_contribuicao_media(ano)
    taxa_fidelidade = random.uniform(*TAXA_FIDELIDADE)
    membros_contribuintes = membros_mes * taxa_fidelidade
    dizimo = membros_contribuintes * contribuicao_media
    dizimo = dizimo * impacto_doacao
    return dizimo

def crescimento_logistico(base, ano, limite=300):
    """
    Calcula crescimento populacional usando modelo logístico.
    """
    k = 0.4
    return limite / (1 + ((limite - base) / base) * (2.718 ** (-k * ano)))

def ajustar_por_membros(valor, categoria, membros_mes):
    """
    Ajusta valores que dependem diretamente da quantidade de membros.
    Exemplo: dízimo.
    """
    if categoria not in CATEGORIAS_DEPENDENTES_MEMBROS:
        return valor

    fator = membros_mes / MEMBROS_INICIAIS
    return valor * fator

def perda_membros():
    """
    Simula perda anual de membros por mudança,
    desmotivação ou rotatividade natural.
    """
    if random.random() < PROB_SAIDA_MEMBRO:
        return random.uniform(*SAIDA_MEMBROS_INTERVALO)
    return 1


# Geradores de Valor
def gerar_valor_categoria(categoria, ano, impacto_doacao, inflacao_anual):
    """
    Gera valor financeiro usando distribuição normal.
    """
    conf = CONFIG_VALORES[categoria]
    media = conf["media_base"]
    desvio = conf["desvio_base"] * (FATOR_VOLATILIDADE_BASE * 0.7)
    crescimento = conf["crescimento_anual"][CENARIO_ATUAL]
    media_ajustada = media * ((1 + crescimento) ** ano) * ((1 + inflacao_anual) ** ano)
    fator = fator_economico()
    valor = max(0, random.gauss(media_ajustada, desvio))
    valor = valor * fator
    
    if conf["tipo"] == "entrada":
        valor = valor * impacto_doacao
    return max(valor, 0)

def aplicar_sazonalidade(valor, mes, categoria):
    """
    Aplica sazonalidade de entradas ou saídas.
    """
    conf = CONFIG_VALORES[categoria]

    if not conf["aplica_sazonal"]:
        return valor

    tipo = conf["tipo"]
    fator = SAZONALIDADE[mes][tipo]
    return valor * fator


# Eventos
def gerar_evento_extra():
    """
    Gera eventos inesperados (custos).
    """
    if random.random() < PROB_EVENTO_EXTRA:
        return random.uniform(
            VALOR_EVENTO_EXTRA[0],
            VALOR_EVENTO_EXTRA[1]
        )
    return 0

def aplicar_evento_especial(mes):
    """
    Eventos planejados no calendário anual.
    """
    if mes not in EVENTOS_ESPECIAIS:
        return 0, 0

    evento = EVENTOS_ESPECIAIS[mes]
    entrada = random.uniform(*evento["entrada_extra"])
    custo = random.uniform(*evento["custo_extra"])
    return entrada, custo

def custo_imprevisto():
    """
    Gera custos inesperados que podem ocorrer durante o ano,
    como manutenção emergencial ou despesas extraordinárias.
    """
    if random.random() < 0.05:
        return random.uniform(800, 5000)
    return 0

def aplicar_contencao_custos(valor, tipo, estado):
    """
    Reduz despesas quando o caixa está abaixo do nível de alerta.
    """

    if tipo == "saida" and estado["caixa"] < CAIXA_ALERTA:
        valor = valor * FATOR_CONTENCAO_CUSTOS

    return valor

def gerar_estado_simulacao(estado_simulacao):
    """
    Atualiza estado econômico do mês.
    """
    duracao = estado_simulacao["duracao_crise"]
    total = estado_simulacao["duracao_crise_total"]

    if duracao <= 0:
        duracao, impacto_doacao, impacto_membros, impacto_custos = crise_global()
        inflacao_anual = inflacao_ano()

        total = duracao
    else:
        duracao -= 1
        impacto_doacao = estado_simulacao["impacto_doacao"]
        impacto_membros = estado_simulacao["impacto_membros"]
        impacto_custos = estado_simulacao["impacto_custos"]
        inflacao_anual = estado_simulacao["inflacao_anual"]

        if total > 0:
            progresso = (total - duracao) / total

            intensidade =  1 - (0.5 * (1 - progresso))

            impacto_doacao = impacto_doacao * intensidade
            impacto_membros = impacto_membros * intensidade
            impacto_custos = impacto_custos * intensidade

    return {
        "duracao_crise": duracao,
        "duracao_crise_total": total,
        "impacto_doacao": impacto_doacao,
        "impacto_membros": impacto_membros,
        "impacto_custos": impacto_custos,
        "inflacao_anual": inflacao_anual
    }

# Motor de Simulação
def gerar_transacoes_mes(ano, mes, estado, estado_simulacao):
    """
    Gera todas as transações do mês. 
    """
    transacoes = []

    impacto_doacao = estado_simulacao["impacto_doacao"]
    impacto_membros = estado_simulacao["impacto_membros"]
    impacto_custos = estado_simulacao["impacto_custos"]
    inflacao_anual = estado_simulacao["inflacao_anual"]

    membros_mes = atualizar_membros(estado, impacto_membros)
    dizimo_base = membros_mes * calcular_contribuicao_media(ano) * impacto_doacao
    dizimo_realista = calcular_dizimo_realista(ano, membros_mes, impacto_doacao)
    dizimo_mes = (dizimo_base * PESO_DIZIMO_BASE + dizimo_realista * PESO_DIZIMO_REALISTA)
    
    for categoria, conf in CONFIG_VALORES.items():

        if categoria == "dizimo":
            valor = dizimo_mes
        else:
            valor = gerar_valor_categoria(categoria, ano, impacto_doacao, inflacao_anual)

        valor = ajustar_por_membros(valor, categoria, membros_mes)

        valor = aplicar_sazonalidade(valor, mes, categoria)
        valor = aplicar_risco_economico(valor)
        
        transacoes.append({
            "categoria": categoria,
            "tipo": conf["tipo"],
            "valor": valor
        })
    return transacoes

def atualizar_caixa(estado, transacoes):
    """
    Atualiza o caixa com base nas transações.
    """
    for t in transacoes:

        if t["tipo"] == "entrada":
            estado["caixa"] += t["valor"]
        else:
            estado["caixa"] -= t["valor"]
    return estado

def atualizar_membros(estado, impacto_membros):
    """
    Atualiza membros mês a mês.
    """
    membros = estado["membros"]
    crescimento = random.uniform(0.001, 0.004)
    saida = random.uniform(0.001, 0.003)
    membros = membros * (1 + crescimento - saida)
    membros = membros * impacto_membros
    membros = min(membros, MEMBROS_LIMITE)
    estado["membros"] = membros
    return membros

def imprimir_resumo_mes(ano, mes, entrada, saida, caixa):
    """
    Mostra resumo do mês (modo debug).
    """
    print(f"Ano {ano + 1} | Mês {mes}")
    print(f"Entradas: {entrada:.2f}")
    print(f"Saídas: {saida:.2f}")
    print(f"Caixa atual: {caixa:.2f}")
    print("-" * 30)

def simular(debug=DEBUG):
    """
    Executa simulação financeira ao longo dos anos definidos.
    """
    estado = iniciar_estado()
    estado_simulacao = iniciar_estado_simulacao()

    for ano in range(ANOS_SIMULACAO):
        
        for mes in range(1, 13):

            estado_simulacao = gerar_estado_simulacao(estado_simulacao)

            if debug and estado_simulacao["duracao_crise"] > 0:
                print(
                    f"CRISE | meses restantes: {estado_simulacao['duracao_crise']} | "
                    f"impacto doação: {estado_simulacao['impacto_doacao']:.2f} | "
                    f"impacto membros: {estado_simulacao['impacto_membros']:.2f}"
                )

            transacoes = gerar_transacoes_mes(ano, mes, estado, estado_simulacao)

            for t in transacoes:

                t["valor"] = aplicar_contencao_custos(
                    t["valor"],
                    t["tipo"],
                    estado
                )

            entrada_total = sum(t["valor"] for t in transacoes if t["tipo"] == "entrada")
            saida_total = sum(t["valor"] for t in transacoes if t["tipo"] == "saida")

            estado = atualizar_caixa(estado, transacoes)

            evento_extra = gerar_evento_extra()
            estado["caixa"] -= evento_extra
            saida_total += evento_extra

            imprevisto = custo_imprevisto()
            estado["caixa"] -= imprevisto
            saida_total += imprevisto

            entrada_extra, custo_extra = aplicar_evento_especial(mes)

            estado["caixa"] += entrada_extra
            entrada_total += entrada_extra

            estado["caixa"] -= custo_extra
            saida_total += custo_extra



            if debug:
                imprimir_resumo_mes(
                        ano,
                        mes,
                        entrada_total,
                        saida_total,
                        estado["caixa"]
                )

            estado["historico"].append({
                "ano": ano,
                "mes": mes,
                "entrada_total": entrada_total,
                "saida_total": saida_total,
                "caixa": estado["caixa"],
                "saldo_mes": entrada_total - saida_total
            })
    return estado


# DataFrame
def gerar_dataframe(resultado):
    """
    Converte histórico da simulação em DataFrame.
    """
    return pd.DataFrame(resultado["historico"])


# Monte Carlo
def analisar_monte_carlo():
    
    df_montecarlo = rodar_monte_carlo()

    plotar_distribuicao_caixa(df_montecarlo)

    media, inferior, superior = gerar_faixa_confianca()
    plotar_faixa_confianca(media, inferior, superior)

    indicadores = calcular_indicadores_risco(df_montecarlo)
    volatilidade = calcular_volatilidade(df_montecarlo)

    df_montecarlo.to_csv("data/02_montecarlo.csv", index=False)

    print("\n==============================")
    print("INDICADORES DE RISCO (Monte Carlo)")
    print("==============================")
    print("Risco de quebra financeira:", round(indicadores["risco_quebra"] * 100, 2), "%")
    print("Caixa médio final:", round(indicadores["caixa_medio"], 2))
    print("Pior cenário:", round(indicadores["pior_caso"], 2))
    print("Melhor cenário:", round(indicadores["melhor_caso"], 2))
    print("Volatilidade financeira:", round(volatilidade, 2))
    
def rodar_monte_carlo():
    """
    Executa várias simulações para análise probabilística.
    """
    resultados = []
    
    for i in range(SIMULACOES_MONTE_CARLO):

        if MONTE_CARLO_LOG_ATIVO and i % MONTE_CARLO_LOG_INTERVALO == 0:
            print("Simulação", i)

        resultado = simular(debug=False)

        quebrou = any(h["caixa"] < CAIXA_MINIMO for h in resultado["historico"])

        resultados.append({
            "simulacao": i,
            "caixa_final": resultado["caixa"],
            "quebrou": quebrou
        })
    return pd.DataFrame(resultados)

def gerar_faixa_confianca():
    """
    Calcula intervalo probabilístico do caixa ao longo do tempo.
    """
    simulacoes = []

    for _ in range(SIMULACOES_MONTE_CARLO):

        resultado = simular(debug=False)
        df = pd.DataFrame(resultado["historico"])
        simulacoes.append(df["caixa"].values)

    matriz = pd.DataFrame(simulacoes)
    media = matriz.mean()
    inferior = matriz.quantile(0.1)
    superior = matriz.quantile(0.9)
    return media, inferior, superior


# Métricas Financeiras
def calcular_indicadores_risco(df_montecarlo):
    """
    Calcula indicadores de risco financeiro com base nas simulações
    Monte Carlo.
    """
    risco_quebra = df_montecarlo["quebrou"].mean()
    caixa_medio = df_montecarlo["caixa_final"].mean()
    pior_caso = df_montecarlo["caixa_final"].min()
    melhor_caso = df_montecarlo["caixa_final"].max()
    return {
        "risco_quebra": risco_quebra,
        "caixa_medio": caixa_medio,
        "pior_caso": pior_caso,
        "melhor_caso": melhor_caso
    }

def mostrar_metricas_financeiras(estado, df):

    runway_meses = calcular_runway(df)
    runway_anos = runway_meses / 12
    taxa_crescimento = calcular_taxa_crescimento(estado)
    margem = calcular_margem(df)
    print("\n==============================")
    print("MÉTRICAS FINANCEIRAS")
    print("==============================")
    print("Runway (meses):", round(runway_meses,1))
    print("Runway (anos):", round(runway_anos,1))
    print("Taxa de crescimento do caixa:", round(taxa_crescimento, 2), "%")
    print("Margem financeira:", round(margem, 2), "%")

def calcular_runway(df):
    """
    Calcula quantos meses a organização sobreviveria
    sem receber novas receitas.
    """
    gasto_medio = df["saida_total"].mean()
    caixa_final = df["caixa"].iloc[-1]
    runway = caixa_final / gasto_medio
    return runway


def calcular_taxa_crescimento(estado):
    """
    Calcula a taxa de crescimento do caixa ao final da simulação.
    """
    return (estado["caixa"] - CAIXA_INICIAL) / CAIXA_INICIAL * 100

def calcular_margem(df):
    """
    Calcula a margem financeira da organização.
    """
    entradas = df["entrada_total"].sum()
    saidas = df["saida_total"].sum()
    return (entradas - saidas) / entradas * 100

def calcular_volatilidade(df_montecarlo):
    """
    Calcula a volatilidade financeira do sistema.
    """
    return df_montecarlo["caixa_final"].std()


# Gráficos
def plotar_caixa(df):
    """
    Evolução do caixa ao longo do tempo.
    """
    plt.figure()
    df["tempo"] = df["ano"] * 12 + df["mes"]
    plt.plot(df["tempo"], df["caixa"])
    plt.title("Evolução do Caixa")
    plt.xlabel("Meses")
    plt.ylabel("Valor")
    plt.savefig("docs/evolucao_caixa.png")
    plt.show()

def plotar_distribuicao_caixa(df):
    """
    Histograma do caixa final das simulações Monte Carlo.
    """
    plt.figure()
    plt.hist(df["caixa_final"], bins=30)
    plt.title("Distribuição do Caixa Final")
    plt.xlabel("Caixa Final")
    plt.ylabel("Frequência")
    plt.savefig("docs/distribuicao_caixa.png")
    plt.show()

def plotar_faixa_confianca(media, inferior, superior):
    """
    Gráfico da faixa de confiança do caixa.
    """
    plt.figure()
    meses = range(len(media))
    plt.plot(meses, media, label="Caixa médio")
    plt.fill_between(meses, inferior, superior, alpha=0.3)
    plt.title("Projeção Probabilística do Caixa")
    plt.xlabel("Meses")
    plt.ylabel("Valor")
    plt.savefig("docs/projecao_probabilistica.png")
    plt.show()


# Resumo Final
def resumo_final(resultado):
    """
    Exibe resumo geral da simulação.
    """
    historico = resultado["historico"]
    entradas = sum(h["entrada_total"] for h in historico)
    saidas = sum(h["saida_total"] for h in historico)
    caixa_final = resultado["caixa"]
    print("\nRESUMO FINAL")
    print("Entradas totais:", round(entradas, 2))
    print("Saídas totais:", round(saidas, 2))
    print("Caixa final:", round(caixa_final, 2))
    return resultado