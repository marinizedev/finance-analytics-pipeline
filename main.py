"""Ponto de entrada do pipeline de simulação financeira."""
import logging
from conf import DEBUG
from logging_config import configurar_logging
from simulation_engine import AnaliseMonteCarlo, GeradorGraficos, SimuladorFinanceiro

logger = logging.getLogger("finance_pipeline.main")


def main() -> None:
    configurar_logging()
    logger.info("Iniciando simulação financeira.")
    simulador = SimuladorFinanceiro()
    resultado = simulador.executar(debug=DEBUG)
    simulacao = resultado.para_dataframe()
    simulacao.to_csv("data/01_simulacao.csv", index=False)

    entradas, saidas = simulacao.entrada_total.sum(), simulacao.saida_total.sum()
    logger.info("Resumo final | Entradas: %.2f | Saídas: %.2f | Caixa: %.2f", entradas, saidas, resultado.caixa)
    logger.info("Métricas | Runway: %.1f meses | Margem: %.2f%%", resultado.caixa / simulacao.saida_total.mean(), (entradas - saidas) / entradas * 100)
    GeradorGraficos.caixa(simulacao)

    analise = AnaliseMonteCarlo(simulador)
    monte_carlo = analise.executar()
    monte_carlo.to_csv("data/02_montecarlo.csv", index=False)
    GeradorGraficos.distribuicao(monte_carlo)
    media, inferior, superior = analise.faixa_confianca()
    GeradorGraficos.faixa_confianca(media, inferior, superior)

    indicadores = analise.indicadores(monte_carlo)
    logger.info("Indicadores de risco | Quebra: %.2f%% | Caixa médio: %.2f | Pior: %.2f | Melhor: %.2f | Volatilidade: %.2f", indicadores["risco_quebra"] * 100, indicadores["caixa_medio"], indicadores["pior_caso"], indicadores["melhor_caso"], indicadores["volatilidade"])
    logger.info("Pipeline concluído com sucesso.")


if __name__ == "__main__":
    main()
