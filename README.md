# FIAP-CCOMP

Repositório de atividades e projetos do curso de Ciência da Computação da FIAP, organizado por ano e fase.

## Atividades

| Ano | Fase | Projeto | Documentação |
| --- | --- | --- | --- |
| 1CCOMP | 1 | Verificação de pré-decolagem da nave AURORA | [Fase 1](1CCOMP/FASE1-ATIVIDADE/README.md) |
| 1CCOMP | 2 | MGPEB — protótipo didático de gerenciamento de módulos e pousos | [Fase 2](1CCOMP/FASE2-ATIVIDADE/README.md) |

### Fase 1 — Verificação de decolagem

Notebook de simulação e análise de telemetria para avaliar as condições de decolagem da nave AURORA. A atividade aborda sensores, integridade estrutural, energia, pressão dos tanques, módulos críticos e autonomia energética.

Utiliza Python, pandas e NumPy. As imagens das execuções estão na pasta `prints/` da atividade.

### Fase 2 — MGPEB

Protótipo em Python 3 do item 3 da atividade integradora, sem bibliotecas externas. Implementa cadastro de dez módulos, buscas lineares, ordenação por prioridade e combustível com Insertion Sort, processamento de fila (FIFO) e pilha de alertas (LIFO).

Na rodada nominal, o programa registra oito pousos e dois alertas. As regras e os limites adotados são hipóteses didáticas; consulte a documentação da fase para os critérios e as limitações da simulação.

## Estrutura do repositório

```text
FIAP-CCOMP/
├── 1CCOMP/
│   ├── FASE1-ATIVIDADE/
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── simulador_decolagem.ipynb
│   │   └── prints/
│   └── FASE2-ATIVIDADE/
│       ├── README.md
│       ├── mgpeb.py
│       ├── test_mgpeb.py
│       └── saida.txt
└── README.md
```

## Como executar

Os comandos abaixo partem da pasta `FIAP-CCOMP`, onde está este README. É necessário ter Python 3 instalado; a Fase 1 também exige um ambiente compatível com notebooks, como Jupyter ou VS Code com suporte a Jupyter.

### Fase 1

Instale as dependências:

```bash
python -m pip install -r 1CCOMP/FASE1-ATIVIDADE/requirements.txt
```

Abra [simulador_decolagem.ipynb](1CCOMP/FASE1-ATIVIDADE/simulador_decolagem.ipynb) no ambiente de notebooks e execute as células em sequência. As instruções detalhadas estão no [README da Fase 1](1CCOMP/FASE1-ATIVIDADE/README.md).

### Fase 2

Execute a simulação:

```bash
python 1CCOMP/FASE2-ATIVIDADE/mgpeb.py
```

Execute os testes:

```bash
python 1CCOMP/FASE2-ATIVIDADE/test_mgpeb.py
```

O arquivo [saida.txt](1CCOMP/FASE2-ATIVIDADE/saida.txt) contém a saída de referência. Consulte o [README da Fase 2](1CCOMP/FASE2-ATIVIDADE/README.md) para os dados, as hipóteses e os resultados esperados.

## Conceitos trabalhados

- Lógica de programação, condicionais e laços.
- Simulação, validação e análise de dados.
- Listas, dicionários, filas e pilhas.
- Busca linear, ordenação e análise de complexidade.
- Testes e documentação de soluções em Python.

Os projetos têm finalidade educacional e documentam as atividades desenvolvidas durante o curso.
