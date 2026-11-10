# Aurora Siger — Sistema de Análise e Decisão da Colônia (Fase 3)

Sistema em Python que organiza os dados dos sensores da colônia, analisa o uso de energia e usa
regressão linear para prever a geração eólica a partir da velocidade do vento.

O objetivo da fase é tirar o sistema do modo reativo (só reagir ao que já aconteceu) e colocá-lo em
modo preditivo: interpretar o histórico dos sensores, antecipar o comportamento das próximas horas e
apoiar a decisão de ligar, reduzir ou desligar cargas.

## Partes do sistema

| Parte | Arquivo | Situação |
| --- | --- | --- |
| Geração dos dados da colônia (clima, geração e consumo de 24 h) | `gerar_dados.py` | Pronto |
| Previsão de geração eólica por regressão linear | `modelo_previsao.py` | Pronto |
| Regras de decisão (priorizar sistemas, reduzir consumo) | `decisao.py` | Em desenvolvimento |
| Análise de energia (geração × consumo × reserva) | `analise_energia.py` | Em desenvolvimento |

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

Requisitos: Python 3 e NumPy (usado apenas na geração dos dados).

```bash
python modelo_previsao.py
```

O bloco `if __name__ == "__main__"` de `modelo_previsao.py` importa o gerador de dados, ajusta o
modelo e mostra a previsão. Se o arquivo de dados tiver outro nome, ajuste apenas a linha
`from gerar_dados import gerar_dados`.

## Exemplo de entrada e saída

Entrada: vento de 11 m/s.

```py
from gerar_dados import gerar_dados
import modelo_previsao as mp

historico = gerar_dados()["historico"]
resultado = mp.executar_previsao(historico, vento_ms=11)
print(resultado["mensagem"])
```

Saída:

```
Equação da reta: y = 0.19 + 2.53 * x
Vento (entrada): 11 m/s
Geração eólica prevista: 28.01 kWh
R²: 0.969 | EMA: 1.12 kWh
Qualidade do ajuste: Excelente
PREVISÃO: com vento de 11 m/s, a geração eólica estimada é de 28.0 kWh (R² = 0.97, ajuste Excelente).
```

Os coeficientes mudam um pouco a cada execução, porque a geração eólica dos dados de teste recebe uma
variação aleatória de -2 a +2 kWh. O resultado fica sempre próximo de 27 kWh para vento de 11 m/s,
que é o valor esperado na atividade.

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

Estas são as regras que o módulo de decisão aplica sobre os dados e as previsões:

- Se energia < 50 kWh, reduzir o consumo.
- Se energia < 50 kWh **e** consumo alto, ativar modo economia.
- Manter sempre ligados os sistemas essenciais (suporte à vida e comunicação) e desligar os não
  essenciais primeiro.
- Se consumo > geração, gerar alerta de risco.
- Se geração > consumo, sugerir armazenamento do excedente na bateria.

Exemplo de entrada e saída de uma regra: entrada `energia = 40, consumo = 70` →
saída `ALERTA: reduzir consumo`.
