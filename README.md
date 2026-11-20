# FIAP-CCOMP

Repositório de atividades e projetos do curso de Ciência da Computação da FIAP. As entregas do primeiro ano estão em `1CCOMP/`, organizadas por fase e Global Solution.

## Projetos do primeiro ano

| Entrega | Projeto | O que você encontra |
| --- | --- | --- |
| Fase 1 | [Verificação de pré-decolagem da nave AURORA](1CCOMP/FASE1-ATIVIDADE/README.md) | Notebook que simula e analisa a telemetria de decolagem, incluindo sensores, integridade estrutural e autonomia energética. |
| Fase 2 | [MGPEB](1CCOMP/FASE2-ATIVIDADE/README.md) | Protótipo em Python para gerenciar módulos e pousos com busca linear, Insertion Sort, fila de processamento e pilha de alertas. |
| Fase 3 | [Aurora Siger](1CCOMP/FASE3-ATIVIDADE/README.md) | Sistema de análise energética da Colônia Aurora. Simula 24 horas de geração e consumo, aplica regras de economia e estima a geração eólica por regressão linear. |
| Global Solution 2026.2 | [Nexcondo](1CCOMP/GLOBAL-SOLUTION-1/README.md) | Help desk de condomínio para registrar e consultar chamados por protocolo, acompanhar a triagem e o histórico e visualizar indicadores de atendimento. |

## Como executar

Execute os comandos a partir da raiz do repositório. Para os notebooks, use o Jupyter ou o VS Code com suporte a Jupyter.

### Fase 1 · Simulador de decolagem

```bash
python -m pip install -r 1CCOMP/FASE1-ATIVIDADE/requirements.txt
```

Abra o [notebook do simulador](1CCOMP/FASE1-ATIVIDADE/simulador_decolagem.ipynb) e execute as células em sequência.

### Fase 2 · MGPEB

O protótipo usa apenas a biblioteca padrão do Python 3. Execute a simulação e os testes com os comandos abaixo.

```bash
python 1CCOMP/FASE2-ATIVIDADE/mgpeb.py
python 1CCOMP/FASE2-ATIVIDADE/test_mgpeb.py
```

A simulação nominal registra oito pousos e dois alertas. Confira a [saída de referência](1CCOMP/FASE2-ATIVIDADE/saida.txt).

### Fase 3 · Aurora Siger

```bash
python -m pip install numpy
python 1CCOMP/FASE3-ATIVIDADE/main.py
python 1CCOMP/FASE3-ATIVIDADE/test_sistema.py
```

O notebook usa também pandas e Matplotlib para gerar tabelas e gráficos. As instruções de instalação estão no [README da Fase 3](1CCOMP/FASE3-ATIVIDADE/README.md#notebook-de-análise). [Notebook de análise de dados](1CCOMP/FASE3-ATIVIDADE/notebooks/analise_dados.ipynb)

### Global Solution · Nexcondo

O sistema de terminal usa Python 3.8 ou superior e a biblioteca padrão. A partir da raiz, entre na pasta do projeto e execute o menu ou os testes.

```bash
cd 1CCOMP/GLOBAL-SOLUTION-1
python src/sistema.py
python -m unittest discover -s tests
```

A opção 10 do menu exporta os dados da sessão e abre o painel web no navegador. A pasta do vídeo inclui o arquivo MP4, as legendas em SRT e os arquivos da composição. [Documentação do vídeo de apresentação](1CCOMP/GLOBAL-SOLUTION-1/VIDEO-NEXCONDO/README.md)

## Estrutura do repositório

```text
FIAP-CCOMP/
├── 1CCOMP/
│   ├── FASE1-ATIVIDADE/
│   ├── FASE2-ATIVIDADE/
│   ├── FASE3-ATIVIDADE/
│   └── GLOBAL-SOLUTION-1/
│       ├── data/
│       ├── docs/
│       ├── src/
│       ├── tests/
│       ├── web/
│       └── VIDEO-NEXCONDO/
└── README.md
```
