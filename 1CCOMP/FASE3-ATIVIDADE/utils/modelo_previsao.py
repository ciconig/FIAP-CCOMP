"""
Módulo de previsão — Fase 3 (A Aurora Estabelece os Primeiros Sistemas da Colônia)

Parte do sistema responsável por prever comportamentos simples da colônia a
partir do histórico de sensores, usando regressão linear (mínimos quadrados),
conforme o Capítulo 7.

Ideia do modelo:
    vento (m/s)  ->  geração eólica (kWh)

A reta ajustada é  y = b0 + b1 * x, calculada com as fórmulas:

    b1 = soma((xi - x_medio) * (yi - y_medio)) / soma((xi - x_medio) ** 2)
    b0 = y_medio - b1 * x_medio

Uso como módulo:

    import modelo_previsao as mp

    modelo = mp.ajustar_reta(ventos, energias)
    previsao = mp.prever(modelo, 11)
"""


# ---------------------------------------------------------------- utilidades

def calcular_media(valores):
    """Média aritmética de uma lista de números."""
    if not valores:
        raise ValueError("Não é possível calcular a média de uma lista vazia.")
    return sum(valores) / len(valores)


def validar_dados(xs, ys):
    """Confere se as duas listas têm o mesmo tamanho e são suficientes."""
    if len(xs) != len(ys):
        raise ValueError("As listas X e Y precisam ter o mesmo tamanho.")
    if len(xs) < 2:
        raise ValueError("São necessários pelo menos 2 pontos para ajustar uma reta.")


# ---------------------------------------------------------- ajuste do modelo

def ajustar_reta(xs, ys):
    """
    Ajusta a reta de regressão pelo método dos mínimos quadrados.

    Retorna um dicionário com os coeficientes e as médias usadas no cálculo:
        {"b0": ..., "b1": ..., "x_medio": ..., "y_medio": ..., "n": ...}
    """
    validar_dados(xs, ys)

    x_medio = calcular_media(xs)
    y_medio = calcular_media(ys)

    soma_produtos = 0.0
    soma_quadrados_x = 0.0

    for x, y in zip(xs, ys):
        desvio_x = x - x_medio
        desvio_y = y - y_medio
        soma_produtos += desvio_x * desvio_y
        soma_quadrados_x += desvio_x ** 2

    if soma_quadrados_x == 0:
        raise ValueError("Todos os valores de X são iguais: a reta não pode ser ajustada.")

    b1 = soma_produtos / soma_quadrados_x
    b0 = y_medio - b1 * x_medio

    return {
        "b0": b0,
        "b1": b1,
        "x_medio": x_medio,
        "y_medio": y_medio,
        "n": len(xs)
    }


def descrever_modelo(modelo):
    """Devolve a equação da reta em texto, ex.: 'y = 1.20 + 2.50 * x'."""
    return "y = {:.2f} + {:.2f} * x".format(modelo["b0"], modelo["b1"])


# --------------------------------------------------------------- previsões

def prever(modelo, x):
    """Estima o valor de Y para um valor de X usando a reta ajustada."""
    return modelo["b0"] + modelo["b1"] * x


def prever_varios(modelo, xs):
    """Estima Y para uma lista de valores de X."""
    return [prever(modelo, x) for x in xs]


def prever_geracao_eolica(modelo, vento_ms):
    """Previsão de geração eólica (kWh) para uma velocidade de vento (m/s)."""
    previsao = prever(modelo, vento_ms)
    return previsao if previsao > 0 else 0.0


def prever_proximas_horas(historico, modelo, quantidade=3):
    """
    Estima a geração eólica das próximas horas repetindo o último vento medido.

    Retorna uma lista de dicionários:
        [{"hora": 24, "vento_ms": ..., "eolica_prevista_kwh": ...}, ...]
    """
    if not historico:
        raise ValueError("Histórico vazio: não há vento para usar como base.")

    ultimo = historico[-1]
    vento_base = ultimo["clima"]["vento_ms"]
    hora_base = ultimo["hora"]

    previsoes = []
    for passo in range(1, quantidade + 1):
        previsoes.append({
            "hora": hora_base + passo,
            "vento_ms": vento_base,
            "eolica_prevista_kwh": prever_geracao_eolica(modelo, vento_base)
        })
    return previsoes


# ------------------------------------------------------- avaliação do modelo

def calcular_residuos(ys, previsoes):
    """Resíduo de cada ponto: valor observado menos valor previsto."""
    validar_dados(ys, previsoes)
    return [y - y_previsto for y, y_previsto in zip(ys, previsoes)]


def calcular_r2(ys, previsoes):
    """
    Coeficiente de determinação (R²): quanto da variação de Y o modelo explica.
    Quanto mais perto de 1, melhor o ajuste.
    """
    validar_dados(ys, previsoes)
    y_medio = calcular_media(ys)

    soma_quadrados_residuos = 0.0
    soma_total_quadrados = 0.0

    for y, y_previsto in zip(ys, previsoes):
        soma_quadrados_residuos += (y - y_previsto) ** 2
        soma_total_quadrados += (y - y_medio) ** 2

    if soma_total_quadrados == 0:
        raise ValueError("Todos os valores de Y são iguais: R² não pode ser calculado.")

    return 1 - (soma_quadrados_residuos / soma_total_quadrados)


def calcular_erro_medio_absoluto(ys, previsoes):
    """Erro médio absoluto (EMA) em kWh: tamanho médio do erro de previsão."""
    validar_dados(ys, previsoes)
    soma_erros = 0.0
    for y, y_previsto in zip(ys, previsoes):
        soma_erros += abs(y - y_previsto)
    return soma_erros / len(ys)


def classificar_ajuste(r2):
    """
    Traduz o R² em uma leitura simples para o operador da colônia
    (estrutura condicional: if / elif / else).
    """
    if r2 >= 0.9:
        return "Excelente"
    elif r2 >= 0.7:
        return "Boa"
    elif r2 >= 0.5:
        return "Moderada"
    else:
        return "Fraca"


def avaliar_modelo(modelo, xs, ys):
    """
    Roda o modelo sobre os dados históricos e devolve o desempenho:
        {"r2": ..., "ema": ..., "qualidade": ..., "residuos": ..., "previsoes": ...}
    """
    previsoes = prever_varios(modelo, xs)
    r2 = calcular_r2(ys, previsoes)
    return {
        "r2": r2,
        "ema": calcular_erro_medio_absoluto(ys, previsoes),
        "qualidade": classificar_ajuste(r2),
        "residuos": calcular_residuos(ys, previsoes),
        "previsoes": previsoes
    }


# ---------------------------------------------------------------- dados base

def extrair_variaveis(historico, variavel_x="vento_ms", variavel_y="eolica_kwh"):
    """
    Monta as duas listas (X e Y) a partir do histórico gerado pelo módulo de dados.

    Exemplos de pares:
        vento_ms      -> eolica_kwh
        irradiancia_wm2 -> solar_kwh
    """
    if not historico:
        raise ValueError("Histórico vazio: não há dados para o modelo.")

    xs = []
    ys = []

    for registro in historico:
        xs.append(registro["clima"][variavel_x])
        ys.append(registro["geracao"][variavel_y])

    return xs, ys


def treinar_modelo_vento(historico):
    """Ajusta o modelo vento -> geração eólica usando o histórico da colônia."""
    ventos, energias = extrair_variaveis(historico, "vento_ms", "eolica_kwh")
    modelo = ajustar_reta(ventos, energias)
    modelo["avaliacao"] = avaliar_modelo(modelo, ventos, energias)
    return modelo


# ---------------------------------------------------- entrada -> saída (API)

def executar_previsao(historico, vento_ms=None):
    """
    Fluxo completo do módulo: entrada -> processamento -> saída.

    Entrada: histórico da colônia e, opcionalmente, um vento a testar.
    Saída: dicionário com o modelo, a previsão e uma mensagem para o operador.
    """
    modelo = treinar_modelo_vento(historico)
    avaliacao = modelo["avaliacao"]

    if vento_ms is None:
        vento_ms = calcular_media(extrair_variaveis(historico, "vento_ms", "eolica_kwh")[0])

    previsao = prever_geracao_eolica(modelo, vento_ms)

    return {
        "equacao": descrever_modelo(modelo),
        "vento_ms": vento_ms,
        "eolica_prevista_kwh": previsao,
        "r2": avaliacao["r2"],
        "ema": avaliacao["ema"],
        "qualidade": avaliacao["qualidade"],
        "mensagem": gerar_mensagem(vento_ms, previsao, avaliacao),
        "proximas_horas": prever_proximas_horas(historico, modelo)
    }


def gerar_mensagem(vento_ms, previsao, avaliacao):
    """Monta a saída em texto, no mesmo estilo dos alertas do sistema."""
    if avaliacao["qualidade"] == "Fraca":
        return (
            "ATENÇÃO: modelo com ajuste fraco (R² = {:.2f}); "
            "usar a previsão apenas como referência.".format(avaliacao["r2"])
        )
    return (
        "PREVISÃO: com vento de {:.0f} m/s, a geração eólica estimada é de "
        "{:.1f} kWh (R² = {:.2f}, ajuste {}).".format(
            vento_ms, previsao, avaliacao["r2"], avaliacao["qualidade"]
        )
    )


# ------------------------------------------------------------------- demo

if __name__ == "__main__":
    # Ajuste o nome abaixo para o arquivo .py que gera os dados da atividade.
    from gerar_dados import gerar_dados

    dados = gerar_dados()
    historico = dados["historico"]

    resultado = executar_previsao(historico, vento_ms=11)

    print("Equação da reta:", resultado["equacao"])
    print("Vento (entrada):", resultado["vento_ms"], "m/s")
    print("Geração eólica prevista:", round(resultado["eolica_prevista_kwh"], 2), "kWh")
    print("R²:", round(resultado["r2"], 3), "| EMA:", round(resultado["ema"], 2), "kWh")
    print("Qualidade do ajuste:", resultado["qualidade"])
    print(resultado["mensagem"])
    print("Próximas horas:")
    for linha in resultado["proximas_horas"]:
        print("  hora {}: vento {} m/s -> {:.1f} kWh".format(
            linha["hora"], linha["vento_ms"], linha["eolica_prevista_kwh"]
        ))
