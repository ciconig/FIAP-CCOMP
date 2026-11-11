# FIAP-CCOMP

Repositório de atividades e projetos do curso de Ciência da Computação da FIAP, organizado por ano e fase.

## Atividades

| Ano | Fase | Projeto | Documentação |
| --- | --- | --- | --- |
| 1CCOMP | 1 | Verificação de pré-decolagem da nave AURORA | [Fase 1](1CCOMP/FASE1-ATIVIDADE/README.md) |
| 1CCOMP | 2 | MGPEB - protótipo didático de gerenciamento de módulos e pousos | [Fase 2](1CCOMP/FASE2-ATIVIDADE/README.md) |
| 1CCOMP | 3 | Aurora Siger - Sistema de Análise e Decisão da Colônia | [Fase 3](1CCOMP/FASE3-ATIVIDADE/README.md) |

### Fase 1 - Verificação de decolagem

Notebook de simulação e análise de telemetria para avaliar as condições de decolagem da nave AURORA. A atividade aborda sensores, integridade estrutural, energia, pressão dos tanques, módulos críticos e autonomia energética.

Utiliza Python, pandas e NumPy. As imagens das execuções estão na pasta `prints/` da atividade.

### Fase 2 - MGPEB

Protótipo em Python 3 do item 3 da atividade integradora, sem bibliotecas externas. Implementa cadastro de dez módulos, buscas lineares, ordenação por prioridade e combustível com Insertion Sort, processamento de fila (FIFO) e pilha de alertas (LIFO).

Na rodada nominal, o programa registra oito pousos e dois alertas. As regras e os limites adotados são hipóteses didáticas; consulte a documentação da fase para os critérios e as limitações da simulação.

### Fase 3 - Aurora Siger

Sistema em Python para organizar dados dos sensores da colônia e prever a geração eólica a partir da velocidade do vento. O gerador utiliza NumPy para criar um histórico de 24 horas com clima, geração solar e eólica, consumo dos sistemas e informações da bateria.

O módulo de previsão implementa regressão linear por mínimos quadrados e avalia o ajuste com R², erro médio absoluto e resíduos. A pasta também inclui um notebook para explorar os dados. As regras de decisão e a análise de energia estão em desenvolvimento, conforme a documentação da fase.

## Estrutura do repositório

```text
FIAP-CCOMP/
├── 1CCOMP/
│   ├── FASE1-ATIVIDADE/
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── simulador_decolagem.ipynb
│   │   └── prints/
│   ├── FASE2-ATIVIDADE/
│   │   ├── README.md
│   │   ├── mgpeb.py
│   │   ├── test_mgpeb.py
│   │   └── saida.txt
│   └── FASE3-ATIVIDADE/
│       ├── .gitignore
│       ├── README.md
│       ├── notebooks/
│       │   └── notebook_teste.ipynb
│       └── utils/
│           ├── gerar_dados.py
│           └── modelo_previsao.py
└── README.md
```

## Como executar

Os comandos abaixo partem da pasta `FIAP-CCOMP`, onde está este README. É necessário ter Python 3 instalado; para executar os notebooks das Fases 1 e 3, utilize um ambiente como Jupyter ou VS Code com suporte a Jupyter.

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

### Fase 3

Instale a dependência do gerador de dados:

```bash
python -m pip install numpy
```

Execute a demonstração de previsão de geração eólica:

```bash
python 1CCOMP/FASE3-ATIVIDADE/utils/modelo_previsao.py
```

Para explorar os dados, abra [notebook_teste.ipynb](1CCOMP/FASE3-ATIVIDADE/notebooks/notebook_teste.ipynb) e execute as células em sequência. Consulte o [README da Fase 3](1CCOMP/FASE3-ATIVIDADE/README.md) para a organização dos dados, as funções do modelo e as regras de decisão previstas.

## Conceitos trabalhados

- Lógica de programação, condicionais e laços.
- Simulação, validação e análise de dados.
- Listas, dicionários, filas e pilhas.
- Busca linear, ordenação e análise de complexidade.
- Organização hierárquica de dados de sensores e simulação energética.
- Regressão linear, previsão e avaliação de modelos com R² e erro médio absoluto.
- Testes e documentação de soluções em Python.

Os projetos têm finalidade educacional e documentam as atividades desenvolvidas durante o curso.
