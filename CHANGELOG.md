# Changelog

Este arquivo registra mudanças relevantes do projeto seguindo o princípio de rastreabilidade: cada versão expõe as decisões, melhorias e impactos técnicos introduzidos.

## [2.4.0] - 2026-09-07

### Adicionado

- Parametrização do crescimento e da saída mensal de membros em `conf.py`.
- Parametrização da probabilidade e da faixa de valor de custos imprevistos.
- Parametrização da duração mínima e máxima de crises econômicas.
- Parametrização da taxa mínima de inflação e do desvio da inflação anual.
- Parametrização do fator econômico base e de sua variação.
- Parametrização dos percentis inferior e superior utilizados na análise de Monte Carlo.
- Cinco novos testes automatizados para validar o uso das configurações no motor de simulação.

### Alterado

- Regras de negócio anteriormente definidas diretamente em `simulation_engine.py` passaram a utilizar parâmetros centralizados em `conf.py`.
- A atualização mensal de membros passou a utilizar faixas configuráveis de crescimento e saída.
- A geração de custos imprevistos passou a utilizar probabilidade e faixa de valor configuráveis.
- A duração das crises econômicas passou a utilizar uma faixa configurável.
- A geração da inflação passou a utilizar limite mínimo e desvio configuráveis.
- O fator econômico passou a utilizar parâmetros configuráveis de valor base e desvio.
- A análise de Monte Carlo passou a utilizar percentis configuráveis para a faixa probabilística.
- A suíte de testes passou de 10 para 15 testes automatizados.

### Removido

- `TAXA_CRESCIMENTO_MEMBROS`, configuração legada sem uso no motor.
- `PROB_SAIDA_MEMBRO`, configuração legada sem uso no motor.
- `SAIDA_MEMBROS_INTERVALO`, configuração legada sem uso no motor.

---

## [2.3.0] - 2026-09-03

### Alterado

- `CRESCIMENTO_CONTRIBUICAO_ANUAL` foi renomeado para `CRESCIMENTO_CONTRIBUICAO_MEDIA_ANUAL`, esclarecendo que afeta a contribuição média por membro.

### Removido

- `CRESCIMENTO_DESPESAS_ANUAL`, configuração legada sem uso no motor.
- Crescimento anual redundante da categoria `dizimo`; o cálculo utiliza exclusivamente o crescimento da contribuição média.

---

## [2.2.0] - 2026-09-03

### Alterado

- Motor de simulação reformatado para priorizar legibilidade, com cálculos e gráficos em etapas nomeadas.
- Importações explícitas substituíram a importação global das configurações.
- O fator econômico voltou a ser um método explícito (`fator_economico`), facilitando leitura e teste isolado.

### Testado

- Adicionado teste que garante a aplicação de `impacto_custos` nos custos durante uma crise.

---

## [2.1.0] - 2026-09-03

### Adicionado

- Configuração centralizada de logging com saída para terminal e arquivo rotativo.
- Parâmetros de nível, caminho, tamanho e retenção de logs em `conf.py`.
- Teste automatizado para garantir que o modo de depuração registre o resumo mensal.

### Alterado

- Todas as mensagens de execução deixaram de usar `print` e passaram a utilizar o módulo `logging`, com níveis de severidade configuráveis.
- Arquivos de log e cache Python passaram a ser ignorados pelo Git.

---

## [2.0.0] - 2026-09-03

### Adicionado

- Modelo orientado a objetos para estado financeiro, estado econômico, transações, registros mensais e resultado de simulação.
- Classes `SimuladorFinanceiro`, `AnaliseMonteCarlo` e `GeradorGraficos`, com responsabilidades explícitas.
- Testes automatizados com `unittest` para regras de caixa, reserva, contenção de custos, eventos, reprodutibilidade e Monte Carlo.
- Documentação da arquitetura V2 e do processo de testes.

### Alterado

- O motor de simulação passou de funções globais e dicionários para objetos do domínio.
- A reserva financeira agora é utilizada quando o caixa fica abaixo do mínimo configurado.
- `main.py` passou a apenas orquestrar o pipeline, deixando a regra de negócio no motor.

### Compatibilidade

- O comando de execução permanece `python main.py`.
- Os datasets continuam sendo gerados em `data/01_simulacao.csv` e `data/02_montecarlo.csv`.
