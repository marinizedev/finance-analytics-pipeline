"""Motor orientado a objetos do simulador financeiro."""

from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass, field
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

from conf import (
    ANOS_SIMULACAO,
    CAIXA_ALERTA,
    CAIXA_INICIAL,
    CAIXA_MINIMO,
    CATEGORIAS_DEPENDENTES_MEMBROS,
    CENARIO_ATUAL,
    CONFIG_VALORES,
    CONTRIBUICAO_MEDIA_INICIAL,
    CRESCIMENTO_CONTRIBUICAO_MEDIA_ANUAL,
    DEBUG,
    DESVIO_CONTRIBUICAO,
    EVENTOS_ESPECIAIS,
    FATOR_CONTENCAO_CUSTOS,
    FATOR_RISCO_ECONOMICO,
    FATOR_VOLATILIDADE_BASE,
    IMPACTO_CUSTOS_CRISE,
    IMPACTO_DOACAO_CRISE,
    IMPACTO_MEMBROS_CRISE,
    MEMBROS_INICIAIS,
    MEMBROS_LIMITE,
    MONTE_CARLO_LOG_ATIVO,
    MONTE_CARLO_LOG_INTERVALO,
    PESO_DIZIMO_BASE,
    PESO_DIZIMO_REALISTA,
    PROB_EVENTO_EXTRA,
    PROBABILIDADE_CRISE,
    RESERVA_INICIAL,
    SAZONALIDADE,
    SIMULACOES_MONTE_CARLO,
    TAXA_FIDELIDADE,
    TAXA_INFLACAO_ANUAL,
    VALOR_EVENTO_EXTRA,
    CRESCIMENTO_MENSAL_MEMBROS,
    SAIDA_MENSAL_MEMBROS,
    DURACAO_CRISE,
    PROB_CUSTO_IMPREVISTO,
    VALOR_CUSTO_IMPREVISTO,
    TAXA_INFLACAO_MINIMA,
    DESVIO_INFLACAO_ANUAL,
    FATOR_ECONOMICO_BASE,
    DESVIO_FATOR_ECONOMICO,
    PERCENTIL_INFERIOR_MONTE_CARLO,
    PERCENTIL_SUPERIOR_MONTE_CARLO,
)

logger = logging.getLogger("finance_pipeline.simulation")


@dataclass
class EstadoFinanceiro:
    """Estado mutável da organização em uma execução da simulação."""

    caixa: float = CAIXA_INICIAL
    reserva: float = RESERVA_INICIAL
    membros: float = MEMBROS_INICIAIS
    historico: list[RegistroMensal] = field(default_factory=list)

    def aplicar(self, transacoes: Iterable[Transacao]) -> None:
        """Aplica entradas e saídas ao caixa."""
        for transacao in transacoes:
            self.caixa += transacao.impacto

    def usar_reserva(self) -> None:
        """Usa a reserva apenas no montante necessário para atingir o mínimo."""
        if self.caixa >= CAIXA_MINIMO or not self.reserva:
            return

        saque = min(CAIXA_MINIMO - self.caixa, self.reserva)
        self.caixa += saque
        self.reserva -= saque


@dataclass
class EstadoEconomico:
    """Condições macroeconômicas vigentes em determinado mês."""

    duracao_crise: int = 0
    duracao_crise_total: int = 0
    impacto_doacao: float = 1.0
    impacto_membros: float = 1.0
    impacto_custos: float = 1.0
    inflacao_anual: float = TAXA_INFLACAO_ANUAL


@dataclass(frozen=True)
class Transacao:
    """Movimentação financeira individual."""

    categoria: str
    tipo: str
    valor: float

    @property
    def impacto(self) -> float:
        """Retorna o impacto assinado da transação no caixa."""
        return self.valor if self.tipo == "entrada" else -self.valor


@dataclass(frozen=True)
class RegistroMensal:
    """Consolidação financeira de um mês simulado."""

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
    """Resultado completo de uma execução do simulador."""

    estado_final: EstadoFinanceiro

    @property
    def caixa(self) -> float:
        return self.estado_final.caixa

    @property
    def historico(self) -> list[RegistroMensal]:
        return self.estado_final.historico

    def para_dataframe(self) -> pd.DataFrame:
        """Converte os registros mensais para um DataFrame analítico."""
        registros = []
        for registro in self.historico:
            registros.append(asdict(registro) | {"saldo_mes": registro.saldo_mes})
        return pd.DataFrame(registros)


class SimuladorFinanceiro:
    """Orquestra regras de membros, economia, transações e caixa."""

    def __init__(
        self,
        anos: int = ANOS_SIMULACAO,
        gerador_aleatorio: random.Random | None = None,
    ) -> None:
        self.anos = anos
        self.rng = gerador_aleatorio or random.Random()

    def executar(self, debug: bool = DEBUG) -> ResultadoSimulacao:
        """Executa a simulação para todos os meses configurados."""
        financeiro = EstadoFinanceiro()
        economia = EstadoEconomico()

        for ano in range(self.anos):
            for mes in range(1, 13):
                economia = self._atualizar_economia(economia)
                transacoes = self._transacoes_mes(ano, mes, financeiro, economia)
                transacoes = [
                    self._conter_custos(transacao, financeiro)
                    for transacao in transacoes
                ]
                eventos = self._eventos(mes)

                financeiro.aplicar(transacoes)
                financeiro.aplicar(eventos)
                financeiro.usar_reserva()

                registro = self._registrar_mes(ano, mes, transacoes, eventos, financeiro)
                financeiro.historico.append(registro)

                if debug:
                    logger.debug(
                        "Ano %s | Mês %s | Caixa: %.2f",
                        ano + 1,
                        mes,
                        financeiro.caixa,
                    )

        return ResultadoSimulacao(financeiro)

    def _registrar_mes(
        self,
        ano: int,
        mes: int,
        transacoes: list[Transacao],
        eventos: list[Transacao],
        estado: EstadoFinanceiro,
    ) -> RegistroMensal:
        movimentacoes = [*transacoes, *eventos]
        entradas = sum(item.valor for item in movimentacoes if item.tipo == "entrada")
        saidas = sum(item.valor for item in movimentacoes if item.tipo == "saida")
        return RegistroMensal(ano, mes, entradas, saidas, estado.caixa)

    def _atualizar_economia(self, anterior: EstadoEconomico) -> EstadoEconomico:
        if anterior.duracao_crise <= 0:
            return self._iniciar_cenario_economico()
        return self._continuar_crise(anterior)

    def _iniciar_cenario_economico(self) -> EstadoEconomico:
        inflacao = max(TAXA_INFLACAO_MINIMA, self.rng.normalvariate(TAXA_INFLACAO_ANUAL, DESVIO_INFLACAO_ANUAL))
        if self.rng.random() >= PROBABILIDADE_CRISE:
            return EstadoEconomico(inflacao_anual=inflacao)

        duracao = self.rng.randint(*DURACAO_CRISE)
        return EstadoEconomico(
            duracao_crise=duracao,
            duracao_crise_total=duracao,
            impacto_doacao=self.rng.uniform(*IMPACTO_DOACAO_CRISE),
            impacto_membros=self.rng.uniform(*IMPACTO_MEMBROS_CRISE),
            impacto_custos=self.rng.uniform(*IMPACTO_CUSTOS_CRISE),
            inflacao_anual=inflacao,
        )

    @staticmethod
    def _continuar_crise(anterior: EstadoEconomico) -> EstadoEconomico:
        duracao_restante = anterior.duracao_crise - 1
        progresso = (
            anterior.duracao_crise_total - duracao_restante
        ) / anterior.duracao_crise_total
        intensidade = 0.5 + 0.5 * progresso

        return EstadoEconomico(
            duracao_crise=duracao_restante,
            duracao_crise_total=anterior.duracao_crise_total,
            impacto_doacao=anterior.impacto_doacao * intensidade,
            impacto_membros=anterior.impacto_membros * intensidade,
            impacto_custos=anterior.impacto_custos * intensidade,
            inflacao_anual=anterior.inflacao_anual,
        )

    def _transacoes_mes(
        self,
        ano: int,
        mes: int,
        estado: EstadoFinanceiro,
        economia: EstadoEconomico,
    ) -> list[Transacao]:
        membros = self._atualizar_membros(estado, economia.impacto_membros)
        dizimo = self._calcular_dizimo(ano, membros, economia.impacto_doacao)
        transacoes = []

        for categoria, configuracao in CONFIG_VALORES.items():
            valor = self._valor_da_categoria(categoria, ano, dizimo, economia)
            valor = self._ajustar_por_membros(valor, categoria, membros)
            valor = self._aplicar_sazonalidade(valor, mes, configuracao)
            valor = self.aplicar_risco_economico(valor)
            transacoes.append(Transacao(categoria, configuracao["tipo"], valor))

        return transacoes

    def _calcular_dizimo(
        self,
        ano: int,
        membros: float,
        impacto_doacao: float,
    ) -> float:
        contribuicao_base = self._contribuicao_media(ano)
        dizimo_base = membros * contribuicao_base * impacto_doacao

        contribuicao_realista = self._contribuicao_media(ano)
        membros_contribuintes = membros * self.rng.uniform(*TAXA_FIDELIDADE)
        dizimo_realista = membros_contribuintes * contribuicao_realista * impacto_doacao

        return (
            dizimo_base * PESO_DIZIMO_BASE
            + dizimo_realista * PESO_DIZIMO_REALISTA
        )

    def _valor_da_categoria(
        self,
        categoria: str,
        ano: int,
        dizimo: float,
        economia: EstadoEconomico,
    ) -> float:
        if categoria == "dizimo":
            return dizimo
        return self._gerar_valor_categoria(categoria, ano, economia)

    def _gerar_valor_categoria(
        self,
        categoria: str,
        ano: int,
        economia: EstadoEconomico,
    ) -> float:
        """Gera o valor base, aplicando inflação e impactos econômicos."""
        configuracao = CONFIG_VALORES[categoria]
        crescimento = configuracao["crescimento_anual"][CENARIO_ATUAL]
        media_ajustada = configuracao["media_base"] * (1 + crescimento) ** ano
        media_ajustada *= (1 + economia.inflacao_anual) ** ano

        desvio = configuracao["desvio_base"] * FATOR_VOLATILIDADE_BASE * 0.7
        valor = max(0, self.rng.gauss(media_ajustada, desvio))
        valor *= self.fator_economico()

        if configuracao["tipo"] == "entrada":
            return valor * economia.impacto_doacao
        return valor * economia.impacto_custos

    def fator_economico(self) -> float:
        """Gera uma oscilação macroeconômica de aproximadamente ±5%."""
        return self.rng.normalvariate(FATOR_ECONOMICO_BASE, DESVIO_FATOR_ECONOMICO)

    @staticmethod
    def aplicar_risco_economico(valor: float) -> float:
        """Aplica o fator de risco global configurado ao valor gerado."""
        return max(0, valor * FATOR_RISCO_ECONOMICO)

    @staticmethod
    def _ajustar_por_membros(valor: float, categoria: str, membros: float) -> float:
        if categoria not in CATEGORIAS_DEPENDENTES_MEMBROS:
            return valor
        return valor * (membros / MEMBROS_INICIAIS)

    @staticmethod
    def _aplicar_sazonalidade(
        valor: float,
        mes: int,
        configuracao: dict,
    ) -> float:
        if not configuracao["aplica_sazonal"]:
            return valor
        return valor * SAZONALIDADE[mes][configuracao["tipo"]]

    def _contribuicao_media(self, ano: int) -> float:
        crescimento = CRESCIMENTO_CONTRIBUICAO_MEDIA_ANUAL[CENARIO_ATUAL]
        media = CONTRIBUICAO_MEDIA_INICIAL * (1 + crescimento) ** ano
        return max(0, self.rng.normalvariate(media, DESVIO_CONTRIBUICAO))

    def _atualizar_membros(self, estado: EstadoFinanceiro, impacto: float) -> float:
        crescimento = self.rng.uniform(*CRESCIMENTO_MENSAL_MEMBROS)
        saida = self.rng.uniform(*SAIDA_MENSAL_MEMBROS)
        membros_atualizados = estado.membros * (1 + crescimento - saida)
        estado.membros = min(membros_atualizados * impacto, MEMBROS_LIMITE)
        return estado.membros

    @staticmethod
    def _conter_custos(transacao: Transacao, estado: EstadoFinanceiro) -> Transacao:
        if transacao.tipo != "saida" or estado.caixa >= CAIXA_ALERTA:
            return transacao

        valor_contido = transacao.valor * FATOR_CONTENCAO_CUSTOS
        return Transacao(transacao.categoria, transacao.tipo, valor_contido)

    def _eventos(self, mes: int) -> list[Transacao]:
        eventos = []

        if self.rng.random() < PROB_EVENTO_EXTRA:
            valor = self.rng.uniform(*VALOR_EVENTO_EXTRA)
            eventos.append(Transacao("evento_extra", "saida", valor))

        if self.rng.random() < PROB_CUSTO_IMPREVISTO:
            valor = self.rng.uniform(*VALOR_CUSTO_IMPREVISTO)
            eventos.append(Transacao("imprevisto", "saida", valor))

        if mes in EVENTOS_ESPECIAIS:
            evento = EVENTOS_ESPECIAIS[mes]
            eventos.extend(
                (
                    Transacao(
                        evento["nome"],
                        "entrada",
                        self.rng.uniform(*evento["entrada_extra"]),
                    ),
                    Transacao(
                        evento["nome"],
                        "saida",
                        self.rng.uniform(*evento["custo_extra"]),
                    ),
                )
            )

        return eventos


class AnaliseMonteCarlo:
    """Repete simulações e produz estatísticas de risco."""

    def __init__(
        self,
        simulador: SimuladorFinanceiro,
        quantidade: int = SIMULACOES_MONTE_CARLO,
    ) -> None:
        self.simulador = simulador
        self.quantidade = quantidade

    def executar(self) -> pd.DataFrame:
        """Executa cenários independentes e consolida o resultado final."""
        resultados = []

        for indice in range(self.quantidade):
            if MONTE_CARLO_LOG_ATIVO and indice % MONTE_CARLO_LOG_INTERVALO == 0:
                logger.info(
                    "Monte Carlo em andamento: simulação %s de %s",
                    indice,
                    self.quantidade,
                )

            resultado = self.simulador.executar()
            quebrou = any(registro.caixa < CAIXA_MINIMO for registro in resultado.historico)
            resultados.append(
                {
                    "simulacao": indice,
                    "caixa_final": resultado.caixa,
                    "quebrou": quebrou,
                }
            )

        return pd.DataFrame(resultados)

    def faixa_confianca(self) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula os percentis configurados do caixa de cada mês."""
        caixas_por_simulacao = []
        for _ in range(self.quantidade):
            resultado = self.simulador.executar()
            caixas_por_simulacao.append(resultado.para_dataframe()["caixa"].to_numpy())

        matriz = pd.DataFrame(caixas_por_simulacao)
        return matriz.mean(), matriz.quantile(PERCENTIL_INFERIOR_MONTE_CARLO), matriz.quantile(PERCENTIL_SUPERIOR_MONTE_CARLO)

    @staticmethod
    def indicadores(resultados: pd.DataFrame) -> dict[str, float]:
        """Calcula os principais indicadores de risco financeiro."""
        return {
            "risco_quebra": resultados["quebrou"].mean(),
            "caixa_medio": resultados["caixa_final"].mean(),
            "pior_caso": resultados["caixa_final"].min(),
            "melhor_caso": resultados["caixa_final"].max(),
            "volatilidade": resultados["caixa_final"].std(),
        }


class GeradorGraficos:
    """Responsável apenas pelas visualizações do pipeline."""

    @staticmethod
    def caixa(
        dados: pd.DataFrame,
        caminho: str = "docs/evolucao_caixa.png",
    ) -> None:
        """Gera o gráfico de evolução mensal do caixa."""
        tempo = dados["ano"] * 12 + dados["mes"]
        plt.figure()
        plt.plot(tempo, dados["caixa"])
        plt.title("Evolução do Caixa")
        plt.xlabel("Meses")
        plt.ylabel("Valor")
        plt.savefig(caminho)
        plt.show()

    @staticmethod
    def distribuicao(
        dados: pd.DataFrame,
        caminho: str = "docs/distribuicao_caixa.png",
    ) -> None:
        """Gera o histograma dos caixas finais do Monte Carlo."""
        plt.figure()
        plt.hist(dados["caixa_final"], bins=30)
        plt.title("Distribuição do Caixa Final")
        plt.xlabel("Caixa Final")
        plt.ylabel("Frequência")
        plt.savefig(caminho)
        plt.show()

    @staticmethod
    def faixa_confianca(
        media: pd.Series,
        inferior: pd.Series,
        superior: pd.Series,
        caminho: str = "docs/projecao_probabilistica.png",
    ) -> None:
        """Gera a faixa probabilística da evolução do caixa."""
        meses = range(len(media))
        plt.figure()
        plt.plot(meses, media, label="Caixa médio")
        plt.fill_between(meses, inferior, superior, alpha=0.3)
        plt.title("Projeção Probabilística do Caixa")
        plt.xlabel("Meses")
        plt.ylabel("Valor")
        plt.savefig(caminho)
        plt.show()
