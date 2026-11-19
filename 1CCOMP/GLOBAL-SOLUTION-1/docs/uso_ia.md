# Uso de inteligência artificial

Ferramentas: Codex (OpenAI) e Claude (Anthropic), em 18/11/2026.

## Como a IA apoiou o desenvolvimento

- **Discussão de ideias:** interpretação do enunciado, escolha do tema (help desk de condomínio) e montagem do plano de divisão das partes.
- **Esclarecimento de conceitos:** fila, pilha, matriz, transições de status e expressões booleanas aplicadas ao sistema.
- **Dados fictícios:** apoio na criação dos chamados e do histórico simulados.
- **Código:** apoio na escrita da validação e leitura dos CSV (`dados.py`), na integração do menu com os módulos de chamados e painel, nos testes automatizados, no tema visual do terminal (`visual.py`) e na interface web (`web/`).
- **Revisão da documentação:** organização e formatação do README.

## Como os resultados foram verificados

- 22 testes automatizados (`python -B -m unittest discover -s tests`) cobrindo dados, chamados e painel, executados em um clone limpo do repositório.
- Execução manual do fluxo do exemplo do enunciado: cadastro, filtro, fila, mudanças de status, últimas atualizações e painel.
- Conferência dos indicadores do README com a saída do sistema.
- Comparação automática dos resultados da interface web (`web/regras.js`) com os do Python (indicadores, matrizes, atrasados e conclusão) e teste das interações no navegador.
- Revisão do código pelos integrantes para entender e justificar cada estrutura e regra antes da gravação do vídeo.
