# Aurora Siger - Sistema de Análise e Decisão da Colônia (Fase 3)

Sistema em Python que organiza os dados dos sensores da colônia, analisa o uso de energia e usa
regressão linear para prever a geração eólica a partir da velocidade do vento.

O objetivo da fase é tirar o sistema do modo reativo (só reagir ao que já aconteceu) e colocá-lo em
modo preditivo: interpretar o histórico dos sensores, antecipar o comportamento das próximas horas e
apoiar a decisão de ligar, reduzir ou desligar cargas.

## Partes do sistema

| Parte | Arquivo | Situação |
| --- | --- | --- |
| Dados da colônia: geração de 24 h, hierarquia e séries | [utils/gerar_dados.py](utils/gerar_dados.py) | Pronto |
| Análise de energia e regras de decisão | [utils/decisoes.py](utils/decisoes.py) | Pronto |
| Previsão de geração eólica por regressão linear | [utils/modelo_previsao.py](utils/modelo_previsao.py) | Pronto |
| Sistema completo pelo terminal (dados → energia → decisões → previsão) | [main.py](main.py) | Pronto |
| Testes (apenas biblioteca padrão e `assert`) | [test_sistema.py](test_sistema.py) | Pronto |
| Análise dos dados com tabelas e gráficos | [notebooks/analise_dados.ipynb](notebooks/analise_dados.ipynb) | Pronto |

Cada módulo cuida de uma parte: `gerar_dados.py` só produz e organiza os dados, `decisoes.py` só aplica
regras e `modelo_previsao.py` só faz a previsão. O `main.py` e o notebook apenas chamam essas funções.

## Notebook de análise dos dados

O [notebook de análise](notebooks/analise_dados.ipynb) reúne o fluxo completo da atividade,
consumindo os dados de `utils/gerar_dados.py`. A semente `np.random.seed(42)` torna os resultados
reproduzíveis. O conteúdo inclui:

- Organização dos sistemas em hierarquia, registros chave-valor e listas paralelas.
- Balanço diário de geração e consumo, classificação das horas de risco e excedente e simulação
  da reserva da bateria, incluindo energia não atendida e excedente não armazenado.
- Regras de decisão com prioridade para suporte à vida e comunicação, além de uma simulação que
  desliga laboratório e lazer em modo economia e recalcula a reserva a cada hora.
- Regressão linear da geração eólica em função do vento e resumo dos resultados com tabelas e gráficos.

As regras de decisão e a regressão são implementadas em Python puro, nos módulos de `utils/`;
pandas e Matplotlib são usados no notebook apenas para organizar tabelas e visualizar os resultados.

## Como os dados são organizados

Os dados ficam em um dicionário hierárquico, separados por assunto (clima, geração, consumo), o que
permite acessar um valor direto pelo caminho, por exemplo `registro["geracao"]["eolica_kwh"]`:

```py
dados = {
    "estrutura": {
        "energia": {"geracao": ["solar", "eolica"], "armazenamento": ["bateria"]},
        "consumidores": {
            "essenciais": ["suporte_vida", "comunicacao"],
            "nao_essenciais": ["laboratorio", "lazer"]
        }
    },
    "bateria": {"capacidade_kwh": 200, "reserva_inicial_kwh": 100},
    "historico": [
        {
            "hora": 0,
            "clima": {"vento_ms": 8, "irradiancia_wm2": 0, "temperatura_c": -55},
            "geracao": {"solar_kwh": 0.0, "eolica_kwh": 20.0, "total_kwh": 20.0},
            "consumo": {"suporte_vida_kwh": 18, "comunicacao_kwh": 4,
                        "laboratorio_kwh": 9, "lazer_kwh": 3, "total_kwh": 34}
        }
        # ... um registro por hora, até 24
    ]
}
```

O `historico` é uma lista de registros horários. É dela que saem as séries usadas na previsão.

## Como funciona a previsão

O modelo usa regressão linear pelo método dos mínimos quadrados, com o vento como variável de
entrada (X) e a geração eólica como variável de saída (Y):

```
b1 = soma((xi - x_medio) * (yi - y_medio)) / soma((xi - x_medio) ** 2)
b0 = y_medio - b1 * x_medio

y = b0 + b1 * x
```

Passo a passo dentro do sistema:

1. `extrair_variaveis(historico)` monta as listas de vento (X) e geração eólica (Y);
2. `ajustar_reta(xs, ys)` calcula `b0` e `b1` e devolve o modelo;
3. `prever(modelo, vento)` estima a geração para um vento novo;
4. `avaliar_modelo(modelo, xs, ys)` calcula o R², o erro médio absoluto e os resíduos, para dizer o
   quanto o modelo é confiável.

A qualidade do ajuste é classificada com regras simples: R² ≥ 0,9 é "Excelente", ≥ 0,7 é "Boa",
≥ 0,5 é "Moderada" e abaixo disso é "Fraca". Com ajuste fraco, a previsão é tratada apenas como
referência.

## Como executar

### Sistema completo pelo terminal

Requisitos: Python 3 e NumPy (`python -m pip install numpy`). A partir da pasta `1CCOMP/FASE3-ATIVIDADE`:

```bash
python main.py          # executa o sistema completo
python test_sistema.py  # executa os testes
```

O `main.py` usa a semente 42, a mesma do notebook, então a saída é sempre igual.

### Notebook de análise

Requisitos: Python 3, NumPy, pandas, Matplotlib e um ambiente com suporte a notebooks Jupyter.
Para instalar as dependências no ambiente Python que será usado pelo notebook:

```bash
python -m pip install numpy pandas matplotlib ipykernel jupyter
```

1. Abra [notebooks/analise_dados.ipynb](notebooks/analise_dados.ipynb) no VS Code com a extensão
   Jupyter ou no Jupyter Notebook/Lab.
2. Selecione o kernel do ambiente Python em que instalou as dependências.
3. Execute todas as células em ordem, desde a primeira, para gerar as tabelas, gráficos e conclusões.

A primeira célula localiza automaticamente `utils/gerar_dados.py` quando executada a partir da
raiz do repositório, da pasta da atividade ou da pasta `notebooks`.

### Módulo de previsão pelo terminal

Para executar apenas a previsão, são necessários Python 3 e NumPy. A partir da pasta
`1CCOMP/FASE3-ATIVIDADE`, execute:

```bash
python utils/modelo_previsao.py
```

O bloco `if __name__ == "__main__"` de `modelo_previsao.py` importa o gerador de dados, ajusta o
modelo e mostra a previsão.

## Exemplo de entrada e saída

Entrada: vento de 11 m/s.

Execute o exemplo abaixo com a pasta `utils` como diretório atual, para importar os módulos locais.

```py
from gerar_dados import gerar_dados
import modelo_previsao as mp

historico = gerar_dados(seed=42)["historico"]
resultado = mp.executar_previsao(historico, vento_ms=11)
print(resultado["equacao"])
print(resultado["mensagem"])
```

Saída:

```
y = -0.15 + 2.55 * x
PREVISÃO: com vento de 11 m/s, a geração eólica estimada é de 27.9 kWh (R² = 0.96, ajuste Excelente).
```

A geração eólica dos dados de teste recebe uma variação aleatória de -2 a +2 kWh. Com `seed=42` a
saída é sempre a mesma; sem semente, os coeficientes mudam um pouco a cada execução, mas o resultado
fica sempre próximo de 27 kWh para vento de 11 m/s, que é o valor esperado na atividade. Com os dados
do próprio enunciado (vento `[8, 10, 12]`, energia `[20, 25, 30]`) a reta é `y = 2.5 * x` e a
previsão para 11 m/s é 27,5 kWh, o que é verificado em `test_sistema.py`.

## Principais funções de `modelo_previsao.py`

| Função | O que faz |
| --- | --- |
| `extrair_variaveis(historico, x, y)` | Monta as listas de X e Y a partir do histórico |
| `ajustar_reta(xs, ys)` | Calcula `b0` e `b1` da reta de regressão |
| `prever(modelo, x)` | Estima um valor de Y para um X |
| `prever_geracao_eolica(modelo, vento_ms)` | Previsão de geração eólica em kWh |
| `prever_proximas_horas(historico, modelo, quantidade)` | Previsão das próximas horas |
| `calcular_r2(ys, previsoes)` | Coeficiente de determinação do modelo |
| `calcular_residuos(ys, previsoes)` | Erro de cada previsão |
| `classificar_ajuste(r2)` | Traduz o R² em Excelente / Boa / Moderada / Fraca |
| `executar_previsao(historico, vento_ms)` | Fluxo completo: entrada → processamento → saída |

## Regras de decisão do sistema

As regras ficam em `decidir()`, em [utils/decisoes.py](utils/decisoes.py). A "energia" do enunciado
corresponde à **reserva da bateria**: é ela que diz quanta energia a colônia ainda tem. As regras são
testadas da mais grave para a mais branda (limites: reserva baixa abaixo de 50 kWh, consumo alto a
partir de 40 kWh/h):

1. Reserva baixa **e** consumo maior que a geração → `ALERTA CRÍTICO`: modo economia, desligar não essenciais.
2. Reserva baixa → `ALERTA`: reduzir consumo.
3. Consumo alto **e** maior que a geração → `ALERTA`: reduzir consumo.
4. Consumo maior que a geração → `ALERTA`: consumo maior que geração.
5. Geração maior que o consumo → `SUGESTÃO`: armazenar o excedente na bateria.
6. Caso contrário → operação normal.

Os sistemas essenciais (suporte à vida e comunicação) nunca são desligados; laboratório e lazer são
cortados primeiro. Exemplos de entrada e saída, como impressos por `python main.py`:

```
geração=40 consumo=70 reserva=100 -> ALERTA: consumo alto e maior que a geração - reduzir consumo
geração=80 consumo=30 reserva=100 -> SUGESTÃO: armazenar energia excedente
geração=20 consumo=60 reserva=30  -> ALERTA CRÍTICO: ativar modo economia e desligar não essenciais
```

## Como o sistema ajuda a melhorar o uso de energia

A energia da colônia é limitada. Nos dados de teste do [notebook de análise](notebooks/analise_dados.ipynb)
(24 h, semente 42), a colônia gera **621 kWh** (475 kWh eólica e 146 kWh solar) e pede **879 kWh**: o
consumo supera a geração em 19 das 24 horas e o dia fecha com déficit de 258 kWh. Sem nenhuma decisão,
a bateria (100 kWh no início) se esgota por volta da hora 5, fica vazia por 14 horas e deixa 158 kWh de
consumo sem atendimento.

O sistema não cria energia: ele melhora **como** ela é usada, em quatro passos.

1. **Organiza** os dados em hierarquia, registros chave-valor e listas paralelas (seção 2 do notebook), para que geração, consumo e reserva possam ser consultados e comparados hora a hora.
2. **Analisa** a geração contra o consumo e acompanha a reserva da bateria (seção 3), apontando as horas de risco e as horas de excedente.
3. **Decide** com prioridade (seção 4, `decidir()` em `utils/decisoes.py`): com a reserva baixa e o consumo acima da geração, ativa o modo economia e desliga laboratório e lazer, mantendo suporte à vida e comunicação.
4. **Prevê** a geração eólica pela regressão linear (seção 5, `utils/modelo_previsao.py`, descrita acima): para vento de 11 m/s o modelo estima 27,9 kWh, próximo dos 27 kWh esperados na atividade, e ajuda a saber quanta energia a colônia pode esperar.

Resultado da simulação de 24 h, sem e com as decisões (seção 4.2 do notebook):

| Indicador | A - sem decisões | B - com decisões |
| --- | --- | --- |
| Consumo considerado | 879 kWh | 691 kWh |
| Consumo não atendido | 158 kWh | 0 kWh |
| Horas com a bateria vazia | 14 h | 0 h |
| Reserva ao final do dia | 0 kWh | 30 kWh |

As decisões reduzem o consumo em 188 kWh (21,4%), todos retirados de laboratório e lazer; os sistemas
essenciais continuam atendidos o dia inteiro e a bateria nunca chega a zero. Em outras palavras, o
sistema troca o consumo não essencial pela garantia de energia para o que mantém a colônia viva.

Limites: os dados são simulados e a previsão ainda não alimenta as regras de decisão, que usam apenas
geração, consumo e reserva da bateria. Ligar as duas partes é o próximo passo natural do projeto.
