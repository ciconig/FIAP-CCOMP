import numpy as np


def criar_estrutura():
    """Representa hierárquica dos sistemas."""
    return {
        "energia": {
            "geracao": ["solar", "eolica"],
            "armazenamento": ["bateria"]
        },
        "consumidores": {
            "essenciais": ["suporte_vida", "comunicacao"],
            "nao_essenciais": ["laboratorio", "lazer"]
        }
    }


def gerar_dados():
    """
    Gera dados para 24 horas.

    Unidades:
    - Vento: m/s
    - Irradiância: W/m²
    - Temperatura: °C
    - Geração, consumo e reserva: kWh
    """
    irradiancia = np.array([
        0, 0, 0, 0, 0, 0,
        50, 100, 200, 300, 400, 500,
        550, 500, 400, 300, 200, 100,
        50, 0, 0, 0, 0, 0
    ])

    # Perfil de vento variado
    vento = np.array([
        8, 10, 12, 6, 4, 5,
        7, 9, 11, 13, 10, 8,
        6, 4, 3, 5, 7, 9,
        11, 12, 10, 8, 6, 4
    ])

    temperatura = np.random.randint(-70, -19, 24)

    suporte_vida = np.random.randint(15, 21, 24)
    comunicacao = np.random.randint(3, 6, 24)
    laboratorio = np.random.randint(5, 16, 24)
    lazer = np.random.randint(2, 9, 24)

    area_paineis = 200
    eficiencia = 0.20
    duracao_horas = 1

    # Energia solar em kWh.
    geracao_solar = (
        irradiancia
        * area_paineis
        * eficiencia
        * duracao_horas
        / 1000
    )

    variacao = np.random.randint(-2, 3, 24)
    geracao_eolica = 2.5 * vento + variacao

    geracao_total = geracao_solar + geracao_eolica

    consumo_total = (
        suporte_vida
        + comunicacao
        + laboratorio
        + lazer
    )

    historico = []

    for hora in range(24):
        registro = {
            "hora": hora,
            "clima": {
                "vento_ms": int(vento[hora]),
                "irradiancia_wm2": int(irradiancia[hora]),
                "temperatura_c": int(temperatura[hora])
            },
            "geracao": {
                "solar_kwh": float(geracao_solar[hora]),
                "eolica_kwh": float(geracao_eolica[hora]),
                "total_kwh": float(geracao_total[hora])
            },
            "consumo": {
                "suporte_vida_kwh": int(suporte_vida[hora]),
                "comunicacao_kwh": int(comunicacao[hora]),
                "laboratorio_kwh": int(laboratorio[hora]),
                "lazer_kwh": int(lazer[hora]),
                "total_kwh": int(consumo_total[hora])
            }
        }

        historico.append(registro)

    dados = {
        "estrutura": criar_estrutura(),
        "bateria": {
            "capacidade_kwh": 200,
            "reserva_inicial_kwh": 100
        },
        "historico": historico
    }

    return dados


def separar_dados_regressao(historico):
    """Retorna listas correspondentes de vento e geração eólica."""
    ventos = []
    energias = []

    for registro in historico:
        ventos.append(registro["clima"]["vento_ms"])
        energias.append(registro["geracao"]["eolica_kwh"])

    return ventos, energias


def exibir_dados(historico):
    """Mostra os registros para conferência."""
    for registro in historico:
        print("Hora:", registro["hora"])
        print("Vento:", registro["clima"]["vento_ms"], "m/s")
        print(
            "Geração solar:",
            registro["geracao"]["solar_kwh"],
            "kWh"
        )
        print(
            "Geração eólica:",
            registro["geracao"]["eolica_kwh"],
            "kWh"
        )
        print(
            "Geração total:",
            registro["geracao"]["total_kwh"],
            "kWh"
        )
        print(
            "Consumo total:",
            registro["consumo"]["total_kwh"],
            "kWh"
        )
        print("------------------------------")


if __name__ == "__main__":
    dados = gerar_dados()

    exibir_dados(dados["historico"])

    ventos, energias = separar_dados_regressao(
        dados["historico"]
    )

    print("Ventos para regressão:", ventos)
    print("Energias para regressão:", energias)