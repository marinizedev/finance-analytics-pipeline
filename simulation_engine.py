"""Motor orientado a objetos do simulador financeiro."""
from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass, field
from typing import Iterable
import matplotlib.pyplot as plt
import pandas as pd
from conf import *

logger = logging.getLogger("finance_pipeline.simulation")


@dataclass
class EstadoFinanceiro:
    """Estado mutável da organização durante uma execução."""
    caixa: float = CAIXA_INICIAL
    reserva: float = RESERVA_INICIAL
    membros: float = MEMBROS_INICIAIS
    historico: list[RegistroMensal] = field(default_factory=list)

    def aplicar(self, transacoes: Iterable[Transacao]) -> None:
        for transacao in transacoes:
            self.caixa += transacao.impacto

    def usar_reserva(self) -> None:
        if self.caixa < CAIXA_MINIMO and self.reserva:
            saque = min(CAIXA_MINIMO - self.caixa, self.reserva)
            self.caixa += saque
            self.reserva -= saque


@dataclass
class EstadoEconomico:
    duracao_crise: int = 0
    duracao_crise_total: int = 0
    impacto_doacao: float = 1.0
    impacto_membros: float = 1.0
    impacto_custos: float = 1.0
    inflacao_anual: float = TAXA_INFLACAO_ANUAL


@dataclass(frozen=True)
class Transacao:
    categoria: str
    tipo: str
    valor: float

    @property
    def impacto(self) -> float:
        return self.valor if self.tipo == "entrada" else -self.valor


@dataclass(frozen=True)
class RegistroMensal:
    ano: int
    mes: int
    entrada_total: float
    saida_total: float
    caixa: float

    @property
    def saldo_mes(self) -> float:
        return self.entrada_total - self.saida_total


@dataclass
class ResultadoSimulacao:
    estado_final: EstadoFinanceiro

    @property
    def caixa(self) -> float:
        return self.estado_final.caixa

    @property
    def historico(self) -> list[RegistroMensal]:
        return self.estado_final.historico

    def para_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(registro) | {"saldo_mes": registro.saldo_mes} for registro in self.historico])


class SimuladorFinanceiro:
    """Orquestra regras de membros, economia, transações e caixa."""
    def __init__(self, anos: int = ANOS_SIMULACAO, gerador_aleatorio: random.Random | None = None):
        self.anos = anos
        self.rng = gerador_aleatorio or random.Random()

    def executar(self, debug: bool = DEBUG) -> ResultadoSimulacao:
        financeiro, economia = EstadoFinanceiro(), EstadoEconomico()
        for ano in range(self.anos):
            for mes in range(1, 13):
                economia = self._atualizar_economia(economia)
                transacoes = [self._conter_custos(t, financeiro) for t in self._transacoes_mes(ano, mes, financeiro, economia)]
                extras = self._eventos(mes)
                financeiro.aplicar(transacoes)
                financeiro.aplicar(extras)
                financeiro.usar_reserva()
                entradas = sum(t.valor for t in (*transacoes, *extras) if t.tipo == "entrada")
                saidas = sum(t.valor for t in (*transacoes, *extras) if t.tipo == "saida")
                registro = RegistroMensal(ano, mes, entradas, saidas, financeiro.caixa)
                financeiro.historico.append(registro)
                if debug:
                    logger.debug("Ano %s | Mês %s | Caixa: %.2f", ano + 1, mes, financeiro.caixa)
        return ResultadoSimulacao(financeiro)

    def _atualizar_economia(self, anterior: EstadoEconomico) -> EstadoEconomico:
        if anterior.duracao_crise <= 0:
            inflacao = max(-0.02, self.rng.normalvariate(TAXA_INFLACAO_ANUAL, .01))
            if self.rng.random() >= PROBABILIDADE_CRISE:
                return EstadoEconomico(inflacao_anual=inflacao)
            duracao = self.rng.randint(3, 12)
            return EstadoEconomico(duracao, duracao, self.rng.uniform(*IMPACTO_DOACAO_CRISE), self.rng.uniform(*IMPACTO_MEMBROS_CRISE), self.rng.uniform(*IMPACTO_CUSTOS_CRISE), inflacao)
        duracao = anterior.duracao_crise - 1
        intensidade = .5 + .5 * ((anterior.duracao_crise_total - duracao) / anterior.duracao_crise_total)
        return EstadoEconomico(duracao, anterior.duracao_crise_total, anterior.impacto_doacao * intensidade, anterior.impacto_membros * intensidade, anterior.impacto_custos * intensidade, anterior.inflacao_anual)

    def _transacoes_mes(self, ano: int, mes: int, estado: EstadoFinanceiro, economia: EstadoEconomico) -> list[Transacao]:
        membros = self._atualizar_membros(estado, economia.impacto_membros)
        dizimo = (membros * self._contribuicao(ano) * economia.impacto_doacao * PESO_DIZIMO_BASE + membros * self.rng.uniform(*TAXA_FIDELIDADE) * self._contribuicao(ano) * economia.impacto_doacao * PESO_DIZIMO_REALISTA)
        transacoes = []
        for categoria, config in CONFIG_VALORES.items():
            valor = dizimo if categoria == "dizimo" else self._valor_categoria(categoria, ano, economia)
            if categoria in CATEGORIAS_DEPENDENTES_MEMBROS:
                valor *= membros / MEMBROS_INICIAIS
            if config["aplica_sazonal"]:
                valor *= SAZONALIDADE[mes][config["tipo"]]
            transacoes.append(Transacao(categoria, config["tipo"], max(0, valor * FATOR_RISCO_ECONOMICO)))
        return transacoes

    def _valor_categoria(self, categoria: str, ano: int, economia: EstadoEconomico) -> float:
        config = CONFIG_VALORES[categoria]
        media = config["media_base"] * (1 + config["crescimento_anual"][CENARIO_ATUAL]) ** ano * (1 + economia.inflacao_anual) ** ano
        valor = max(0, self.rng.gauss(media, config["desvio_base"] * FATOR_VOLATILIDADE_BASE * .7)) * self.rng.normalvariate(1, .05)
        return valor * (economia.impacto_doacao if config["tipo"] == "entrada" else economia.impacto_custos)

    def _contribuicao(self, ano: int) -> float:
        media = CONTRIBUICAO_MEDIA_INICIAL * (1 + CRESCIMENTO_CONTRIBUICAO_ANUAL[CENARIO_ATUAL]) ** ano
        return max(0, self.rng.normalvariate(media, DESVIO_CONTRIBUICAO))

    def _atualizar_membros(self, estado: EstadoFinanceiro, impacto: float) -> float:
        estado.membros = min(estado.membros * (1 + self.rng.uniform(.001, .004) - self.rng.uniform(.001, .003)) * impacto, MEMBROS_LIMITE)
        return estado.membros

    @staticmethod
    def _conter_custos(transacao: Transacao, estado: EstadoFinanceiro) -> Transacao:
        if transacao.tipo == "saida" and estado.caixa < CAIXA_ALERTA:
            return Transacao(transacao.categoria, transacao.tipo, transacao.valor * FATOR_CONTENCAO_CUSTOS)
        return transacao

    def _eventos(self, mes: int) -> list[Transacao]:
        eventos = []
        if self.rng.random() < PROB_EVENTO_EXTRA:
            eventos.append(Transacao("evento_extra", "saida", self.rng.uniform(*VALOR_EVENTO_EXTRA)))
        if self.rng.random() < .05:
            eventos.append(Transacao("imprevisto", "saida", self.rng.uniform(800, 5000)))
        if mes in EVENTOS_ESPECIAIS:
            evento = EVENTOS_ESPECIAIS[mes]
            eventos += [Transacao(evento["nome"], "entrada", self.rng.uniform(*evento["entrada_extra"])), Transacao(evento["nome"], "saida", self.rng.uniform(*evento["custo_extra"]))]
        return eventos


class AnaliseMonteCarlo:
    """Repete simulações e produz estatísticas de risco."""
    def __init__(self, simulador: SimuladorFinanceiro, quantidade: int = SIMULACOES_MONTE_CARLO):
        self.simulador, self.quantidade = simulador, quantidade

    def executar(self) -> pd.DataFrame:
        resultados = []
        for indice in range(self.quantidade):
            if MONTE_CARLO_LOG_ATIVO and indice % MONTE_CARLO_LOG_INTERVALO == 0:
                logger.info("Monte Carlo em andamento: simulação %s de %s", indice, self.quantidade)
            resultado = self.simulador.executar()
            resultados.append({"simulacao": indice, "caixa_final": resultado.caixa, "quebrou": any(r.caixa < CAIXA_MINIMO for r in resultado.historico)})
        return pd.DataFrame(resultados)

    def faixa_confianca(self) -> tuple[pd.Series, pd.Series, pd.Series]:
        matriz = pd.DataFrame([self.simulador.executar().para_dataframe()["caixa"].to_numpy() for _ in range(self.quantidade)])
        return matriz.mean(), matriz.quantile(.1), matriz.quantile(.9)

    @staticmethod
    def indicadores(df: pd.DataFrame) -> dict[str, float]:
        return {"risco_quebra": df.quebrou.mean(), "caixa_medio": df.caixa_final.mean(), "pior_caso": df.caixa_final.min(), "melhor_caso": df.caixa_final.max(), "volatilidade": df.caixa_final.std()}


class GeradorGraficos:
    """Responsável apenas pelas visualizações do pipeline."""
    @staticmethod
    def caixa(df: pd.DataFrame, caminho="docs/evolucao_caixa.png"):
        plt.figure(); plt.plot(df.ano * 12 + df.mes, df.caixa); plt.title("Evolução do Caixa"); plt.xlabel("Meses"); plt.ylabel("Valor"); plt.savefig(caminho); plt.show()
    @staticmethod
    def distribuicao(df: pd.DataFrame, caminho="docs/distribuicao_caixa.png"):
        plt.figure(); plt.hist(df.caixa_final, bins=30); plt.title("Distribuição do Caixa Final"); plt.xlabel("Caixa Final"); plt.ylabel("Frequência"); plt.savefig(caminho); plt.show()
    @staticmethod
    def faixa_confianca(media, inferior, superior, caminho="docs/projecao_probabilistica.png"):
        plt.figure(); plt.plot(range(len(media)), media, label="Caixa médio"); plt.fill_between(range(len(media)), inferior, superior, alpha=.3); plt.title("Projeção Probabilística do Caixa"); plt.xlabel("Meses"); plt.ylabel("Valor"); plt.savefig(caminho); plt.show()
