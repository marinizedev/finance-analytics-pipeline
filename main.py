from simulation_engine import *

def main():
    """
    Função principal que orquestra toda a execução do sistema de simulação financeira.
    """
    print("Iniciando simulação financeira...\n")
    
    resultado = simular(debug=DEBUG)

    resumo_final(resultado)

    df_simulacao = gerar_dataframe(resultado)

    df_simulacao.to_csv("data/01_simulacao.csv", index=False)
    
    mostrar_metricas_financeiras(resultado, df_simulacao)

    plotar_caixa(df_simulacao)
    
    analisar_monte_carlo()
    
if __name__ == "__main__":
    main()