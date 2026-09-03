# Changelog

Este arquivo registra mudanças relevantes do projeto seguindo o princípio de rastreabilidade: cada versão expõe as decisões, melhorias e impactos técnicos introduzidos.

## [2.1.0] - 2026-09-03

### Adicionado

- Configuração centralizada de logging com saída para terminal e arquivo rotativo.
- Parâmetros de nível, caminho, tamanho e retenção de logs em `conf.py`.
- Teste automatizado para garantir que o modo de depuração registre o resumo mensal.

### Alterado

- Todas as mensagens de execução deixaram de usar `print` e passaram a usar logs estruturados por nível.
- Arquivos de log e cache Python passaram a ser ignorados pelo Git.

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
