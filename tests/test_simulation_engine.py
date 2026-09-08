"""Testes das regras críticas do simulador financeiro."""

import random
import unittest

from unittest.mock import patch

from conf import CAIXA_MINIMO, CONFIG_VALORES, EVENTOS_ESPECIAIS

from simulation_engine import (
AnaliseMonteCarlo,
EstadoFinanceiro,
EstadoEconomico,
SimuladorFinanceiro,
Transacao,
)

class GeradorSemEventosAleatorios:
    """RNG controlado: permite testar somente os eventos do calendário."""

    def random(self):
        return 0.99

    def uniform(self, inferior, superior):
        return (inferior + superior) / 2

class EstadoFinanceiroTests(unittest.TestCase):

    def test_aplicar_transacoes_atualiza_caixa_por_tipo(self):
        estado = EstadoFinanceiro(caixa=1_000)
        estado.aplicar((
            Transacao("oferta", "entrada", 250),
            Transacao("aluguel", "saida", 400),
        ))

        self.assertEqual(estado.caixa, 850)

    def test_reserva_cobre_apenas_o_necessario_para_o_caixa_minimo(self):
        estado = EstadoFinanceiro(caixa=1_500, reserva=1_000)
        estado.usar_reserva()

        self.assertEqual(estado.caixa, CAIXA_MINIMO)
        self.assertEqual(estado.reserva, 500)

    def test_reserva_nao_deixa_o_caixa_abaixo_do_valor_disponivel(self):
        estado = EstadoFinanceiro(caixa=0, reserva=800)
        estado.usar_reserva()

        self.assertEqual(estado.caixa, 800)
        self.assertEqual(estado.reserva, 0)


class SimuladorFinanceiroTests(unittest.TestCase):

    def test_simulacao_de_um_ano_gera_doze_registros_e_dataframe(self):
        resultado = SimuladorFinanceiro(
            anos=1,
            gerador_aleatorio=random.Random(42),
        ).executar()

        dataframe = resultado.para_dataframe()

        self.assertEqual(len(resultado.historico), 12)
        self.assertEqual(
            list(dataframe.columns),
            [
                "ano",
                "mes",
                "entrada_total",
                "saida_total",
                "caixa",
                "saldo_mes",
            ],
        )
        self.assertTrue((dataframe["entrada_total"] >= 0).all())
        self.assertTrue((dataframe["saida_total"] >= 0).all())

    def test_semente_igual_produz_resultado_reproduzivel(self):
        primeiro = SimuladorFinanceiro(
            anos=1,
            gerador_aleatorio=random.Random(123),
        ).executar()

        segundo = SimuladorFinanceiro(
            anos=1,
            gerador_aleatorio=random.Random(123),
        ).executar()

        self.assertEqual(
            primeiro.para_dataframe().to_dict(),
            segundo.para_dataframe().to_dict(),
        )

    def test_modo_debug_registra_o_resumo_de_cada_mes_no_logger(self):
        simulador = SimuladorFinanceiro(
            anos=1,
            gerador_aleatorio=random.Random(42),
        )

        with self.assertLogs(
            "finance_pipeline.simulation",
            level="DEBUG",
        ) as logs:
            simulador.executar(debug=True)

        self.assertEqual(len(logs.output), 12)
        self.assertIn("Ano 1 | Mês 1", logs.output[0])

    def test_contencao_reduz_apenas_transacoes_de_saida_com_caixa_em_alerta(self):
        estado = EstadoFinanceiro(caixa=0)

        saida = SimuladorFinanceiro._conter_custos(
            Transacao("aluguel", "saida", 100),
            estado,
        )

        entrada = SimuladorFinanceiro._conter_custos(
            Transacao("oferta", "entrada", 100),
            estado,
        )

        self.assertEqual(saida.valor, 80)
        self.assertEqual(entrada.valor, 100)

    def test_evento_planejado_cria_uma_entrada_e_uma_saida(self):
        simulador = SimuladorFinanceiro(
            gerador_aleatorio=GeradorSemEventosAleatorios(),
        )

        eventos = simulador._eventos(3)

        self.assertEqual(len(eventos), 2)
        self.assertEqual(
            [evento.tipo for evento in eventos],
            ["entrada", "saida"],
        )
        self.assertEqual(
            [evento.categoria for evento in eventos],
            [EVENTOS_ESPECIAIS[3]["nome"]] * 2,
        )

    def test_crise_aplica_impacto_aos_custos(self):
        simulador = SimuladorFinanceiro(
            gerador_aleatorio=random.Random(1),
        )

        economia_base = EstadoEconomico(
            inflacao_anual=0,
            impacto_custos=1,
        )

        economia_em_crise = EstadoEconomico(
            inflacao_anual=0,
            impacto_custos=1.25,
        )

        with patch.object(
            SimuladorFinanceiro,
            "fator_economico",
            return_value=1,
        ):
            custo_base = simulador._gerar_valor_categoria(
                "aluguel",
                0,
                economia_base,
            )

            custo_em_crise = simulador._gerar_valor_categoria(
                "aluguel",
                0,
                economia_em_crise,
            )

        self.assertEqual(
            custo_base,
            CONFIG_VALORES["aluguel"]["media_base"],
        )
        self.assertEqual(
            custo_em_crise,
            custo_base * 1.25,
        )

    def test_atualizacao_de_membros_usa_as_faixas_configuradas(self):
        class GeradorMembros:
            def uniform(self, inferior, superior):
                return (inferior + superior) / 2

        simulador = SimuladorFinanceiro(
            gerador_aleatorio=GeradorMembros(),
        )

        estado = EstadoFinanceiro(membros=100)

        with patch(
            "simulation_engine.CRESCIMENTO_MENSAL_MEMBROS",
            (0.001, 0.004),
        ), patch(
            "simulation_engine.SAIDA_MENSAL_MEMBROS",
            (0.001, 0.003),
        ):
            membros = simulador._atualizar_membros(
                estado,
                impacto=1,
            )

        crescimento_medio = (0.001 + 0.004) / 2
        saida_media = (0.001 + 0.003) / 2

        esperado = 100 * (
            1 + crescimento_medio - saida_media
        )

        self.assertEqual(membros, esperado)

    def test_custo_imprevisto_respeita_probabilidade_configurada(self):
        class GeradorCustoImprevisto:
            def random(self):
                return 0.01

            def uniform(self, inferior, superior):
                return inferior

        simulador = SimuladorFinanceiro(
            gerador_aleatorio=GeradorCustoImprevisto(),
        )

        with patch(
            "simulation_engine.PROB_CUSTO_IMPREVISTO",
            0.02,
        ):
            eventos = simulador._eventos(1)

        categorias = [evento.categoria for evento in eventos]

        self.assertIn("imprevisto", categorias)

    def test_custo_imprevisto_respeita_faixa_de_valor_configurada(self):
        class GeradorCustoImprevisto:
            def random(self):
                return 0.01

            def uniform(self, inferior, superior):
                return superior

        simulador = SimuladorFinanceiro(
            gerador_aleatorio=GeradorCustoImprevisto(),
        )

        with patch(
            "simulation_engine.PROB_CUSTO_IMPREVISTO",
            0.02,
        ), patch(
            "simulation_engine.VALOR_CUSTO_IMPREVISTO",
            (800, 5000),
        ):
            eventos = simulador._eventos(1)

        imprevistos = [
            evento
            for evento in eventos
            if evento.categoria == "imprevisto"
        ]

        self.assertEqual(len(imprevistos), 1)
        self.assertEqual(imprevistos[0].valor, 5000)

    def test_duracao_da_crise_usa_a_faixa_configurada(self):
        class GeradorComCrise:
            def random(self):
                return 0.01

            def uniform(self, inferior, superior):
                return (inferior + superior) / 2

            def randint(self, inferior, superior):
                return superior

            def normalvariate(self, media, desvio):
                return media

        simulador = SimuladorFinanceiro(
            gerador_aleatorio=GeradorComCrise(),
        )

        with patch(
            "simulation_engine.PROBABILIDADE_CRISE",
            0.02,
        ), patch(
            "simulation_engine.DURACAO_CRISE",
            (3, 12),
        ):
            economia = simulador._iniciar_cenario_economico()

        self.assertEqual(economia.duracao_crise, 12)
        self.assertEqual(economia.duracao_crise_total, 12)

    def test_fator_economico_usa_parametros_configurados(self):
        class GeradorFatorEconomico:
            def normalvariate(self, media, desvio):
                return media + desvio

        simulador = SimuladorFinanceiro(
            gerador_aleatorio=GeradorFatorEconomico(),
        )

        with patch(
            "simulation_engine.FATOR_ECONOMICO_BASE",
            1.0,
        ), patch(
            "simulation_engine.DESVIO_FATOR_ECONOMICO",
            0.05,
        ):
            fator = simulador.fator_economico()

        self.assertEqual(fator, 1.05)

class AnaliseMonteCarloTests(unittest.TestCase):

    def test_analise_retorna_uma_linha_por_simulacao_e_indicadores(self):
        simulador = SimuladorFinanceiro(
            anos=1,
            gerador_aleatorio=random.Random(10),
        )

        resultados = AnaliseMonteCarlo(
            simulador,
            quantidade=3,
        ).executar()

        indicadores = AnaliseMonteCarlo.indicadores(resultados)

        self.assertEqual(len(resultados), 3)
        self.assertEqual(
            set(resultados.columns),
            {"simulacao", "caixa_final", "quebrou"},
        )
        self.assertEqual(
            set(indicadores),
            {
                "risco_quebra",
                "caixa_medio",
                "pior_caso",
                "melhor_caso",
                "volatilidade",
            },
        )

if __name__ == "__main__":
    unittest.main()