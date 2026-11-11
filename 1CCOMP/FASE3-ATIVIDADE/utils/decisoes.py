"""
Módulo de decisões e análise de energia — Fase 3

Separa as regras de decisão (lógica do sistema) dos dados e da previsão.
Python puro: recebe números e listas e devolve decisões em texto ou
registros (dicionários), sem depender de pandas.

Uso como módulo:

    import decisoes as dc

    dc.decidir(geracao_kwh=40, consumo_kwh=70, reserva_kwh=30)
"""

LIMITE_RESERVA = 50     # kWh - abaixo disso a energia (reserva da bateria) é considerada baixa
CONSUMO_ALTO = 40       # kWh/hora - acima disso o consumo é considerado alto

ESSENCIAIS = ["suporte_vida", "comunicacao"]
NAO_ESSENCIAIS = ["laboratorio", "lazer"]


# --------------------------------------------------------- análise de energia

def classificar_balanco(geracao, consumo):
    """Compara geração e consumo e devolve a situação da hora."""
    if consumo > geracao:
        return "RISCO: consumo maior que geração"
    elif geracao > consumo:
        return "SUGESTÃO: armazenar energia excedente"
    return "EQUILÍBRIO: geração igual ao consumo"


def simular_bateria(series, capacidade_kwh, reserva_inicial_kwh):
    """
    Percorre as 24 horas atualizando a reserva da bateria.

    Recebe as séries paralelas de gerar_dados.extrair_series e devolve uma
    lista de registros por hora:
        [{"hora": ..., "reserva_kwh": ..., "excedente_perdido_kwh": ...,
          "deficit_nao_atendido_kwh": ...}, ...]
    """
    reserva = reserva_inicial_kwh
    simulacao = []

    for hora, geracao, consumo in zip(
        series["hora"], series["geracao_kwh"], series["consumo_kwh"]
    ):
        saldo = geracao - consumo
        excedente_perdido = 0.0
        deficit_nao_atendido = 0.0

        if saldo >= 0:
            nova_reserva = min(capacidade_kwh, reserva + saldo)
            excedente_perdido = (reserva + saldo) - nova_reserva
            reserva = nova_reserva
        else:
            deficit_nao_atendido = abs(min(0.0, reserva + saldo))
            reserva = max(0.0, reserva + saldo)

        simulacao.append({
            "hora": hora,
            "reserva_kwh": reserva,
            "excedente_perdido_kwh": excedente_perdido,
            "deficit_nao_atendido_kwh": deficit_nao_atendido,
        })

    return simulacao


# --------------------------------------------------------- regras de decisão

def decidir(geracao_kwh, consumo_kwh, reserva_kwh,
            limite_reserva=LIMITE_RESERVA, consumo_alto=CONSUMO_ALTO):
    """
    Aplica as regras de decisão e devolve a ação (saída do sistema).

    "Energia" no enunciado corresponde aqui à reserva da bateria: é ela que
    diz quanta energia a colônia ainda tem disponível.
    As regras são testadas da mais grave para a mais branda.
    """
    if reserva_kwh < limite_reserva and consumo_kwh > geracao_kwh:
        return "ALERTA CRÍTICO: ativar modo economia e desligar não essenciais"
    if reserva_kwh < limite_reserva:
        return "ALERTA: reserva baixa - reduzir consumo"
    if consumo_kwh >= consumo_alto and consumo_kwh > geracao_kwh:
        return "ALERTA: consumo alto e maior que a geração - reduzir consumo"
    if consumo_kwh > geracao_kwh:
        return "ALERTA: consumo maior que geração"
    if geracao_kwh > consumo_kwh:
        return "SUGESTÃO: armazenar energia excedente"
    return "EQUILÍBRIO: manter operação normal"


def acoes_por_decisao(decisao, essenciais=ESSENCIAIS, nao_essenciais=NAO_ESSENCIAIS):
    """Traduz a decisão em ações, mantendo os sistemas essenciais ligados."""
    if decisao.startswith("ALERTA CRÍTICO"):
        return [f"manter {sistema} ligado" for sistema in essenciais] + \
               [f"desligar {sistema}" for sistema in nao_essenciais]
    if decisao.startswith("ALERTA"):
        return [f"manter {sistema} ligado" for sistema in essenciais] + \
               ["reduzir carga do laboratório"]
    if decisao.startswith("SUGESTÃO"):
        return ["carregar a bateria com o excedente"]
    return ["manter operação normal"]


def simular_dia_com_decisoes(historico, capacidade_kwh, reserva_inicial_kwh):
    """
    Repete o dia com o sistema reagindo: modo economia corta os não essenciais.

    Devolve uma lista de registros por hora com consumo ajustado, reserva,
    consumo não atendido e a decisão tomada.
    """
    reserva = reserva_inicial_kwh
    resultado = []

    for registro in historico:
        geracao = registro["geracao"]["total_kwh"]
        consumo_base = registro["consumo"]["total_kwh"]
        decisao = decidir(geracao, consumo_base, reserva)

        consumo = consumo_base
        if decisao.startswith("ALERTA CRÍTICO"):
            # mantém apenas suporte à vida e comunicação
            consumo = (registro["consumo"]["suporte_vida_kwh"]
                       + registro["consumo"]["comunicacao_kwh"])
        elif decisao.startswith("ALERTA"):
            # reduz o laboratório pela metade
            consumo = consumo_base - registro["consumo"]["laboratorio_kwh"] / 2

        saldo = geracao - consumo
        deficit_nao_atendido = 0.0
        if saldo >= 0:
            reserva = min(capacidade_kwh, reserva + saldo)
        else:
            deficit_nao_atendido = abs(min(0.0, reserva + saldo))
            reserva = max(0.0, reserva + saldo)

        resultado.append({
            "hora": registro["hora"],
            "geracao_kwh": geracao,
            "consumo_base_kwh": consumo_base,
            "consumo_kwh": consumo,
            "reserva_kwh": reserva,
            "deficit_nao_atendido_kwh": deficit_nao_atendido,
            "decisao": decisao,
        })

    return resultado
