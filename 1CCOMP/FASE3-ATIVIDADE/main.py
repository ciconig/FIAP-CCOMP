"""
Aurora Siger — Sistema de Análise e Decisão da Colônia (Fase 3)

Executa o sistema completo pelo terminal, em quatro etapas:
    1. organizar os dados da colônia (hierarquia, chave-valor e listas);
    2. analisar o uso de energia (geração x consumo e reserva da bateria);
    3. tomar decisões automáticas a partir das regras;
    4. prever a geração eólica por regressão linear.

Execute a partir da pasta 1CCOMP/FASE3-ATIVIDADE:
    python main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "utils"))

import gerar_dados as gd       # noqa: E402  (dados)
import decisoes as dc          # noqa: E402  (análise de energia e decisões)
import modelo_previsao as mp   # noqa: E402  (previsão)

SEED = 42  # mesma semente do notebook: resultados reproduzíveis


def titulo(texto):
    print()
    print(texto)
    print("=" * len(texto))


def etapa_dados(dados):
    titulo("1. ORGANIZAÇÃO DOS DADOS")
    print("Hierarquia dos sistemas:")
    gd.mostrar_hierarquia(dados["estrutura"])

    registro = dados["historico"][12]
    print("\nRegistro chave-valor (hora {}):".format(registro["hora"]))
    for grupo in ("clima", "geracao", "consumo"):
        print("  [{}] {}".format(grupo, registro[grupo]))

    series = gd.extrair_series(dados["historico"])
    print("\nListas paralelas: {} horas de {}".format(
        len(series["hora"]), ", ".join(chave for chave in series if chave != "hora")
    ))
    return series


def etapa_energia(dados, series):
    titulo("2. ANÁLISE DO USO DE ENERGIA")
    geracao_total = sum(series["geracao_kwh"])
    consumo_total = sum(series["consumo_kwh"])
    saldo = geracao_total - consumo_total
    print("Geração do dia: {:6.1f} kWh | Consumo do dia: {:6.1f} kWh | Saldo: {:+.1f} kWh".format(
        geracao_total, consumo_total, saldo))

    situacoes = {}
    for geracao, consumo in zip(series["geracao_kwh"], series["consumo_kwh"]):
        situacao = dc.classificar_balanco(geracao, consumo)
        situacoes[situacao] = situacoes.get(situacao, 0) + 1
    for situacao, horas in situacoes.items():
        print("  {:2d} h  {}".format(horas, situacao))

    bateria = dados["bateria"]
    simulacao = dc.simular_bateria(series, bateria["capacidade_kwh"], bateria["reserva_inicial_kwh"])
    reservas = [hora["reserva_kwh"] for hora in simulacao]
    print("Reserva da bateria: inicial {:.0f} kWh | mínima {:.1f} kWh | final {:.1f} kWh".format(
        bateria["reserva_inicial_kwh"], min(reservas), reservas[-1]))
    print("Consumo não atendido: {:.1f} kWh | Excedente não armazenado: {:.1f} kWh".format(
        sum(hora["deficit_nao_atendido_kwh"] for hora in simulacao),
        sum(hora["excedente_perdido_kwh"] for hora in simulacao)))
    return simulacao


def etapa_decisoes(dados, simulacao):
    titulo("3. DECISÕES AUTOMÁTICAS")
    print("Exemplos do enunciado (entrada -> saída):")
    exemplos = [(40, 70, 100), (80, 30, 100), (20, 60, 30)]
    for geracao, consumo, reserva in exemplos:
        decisao = dc.decidir(geracao, consumo, reserva)
        print("  geração={} consumo={} reserva={} -> {}".format(geracao, consumo, reserva, decisao))
        print("      ações: {}".format(", ".join(dc.acoes_por_decisao(decisao))))

    contagem = {}
    for registro, hora in zip(dados["historico"], simulacao):
        decisao = dc.decidir(registro["geracao"]["total_kwh"],
                             registro["consumo"]["total_kwh"], hora["reserva_kwh"])
        contagem[decisao] = contagem.get(decisao, 0) + 1
    print("\nDecisões ao longo das 24 h:")
    for decisao, horas in contagem.items():
        print("  {:2d} h  {}".format(horas, decisao))

    bateria = dados["bateria"]
    controle = dc.simular_dia_com_decisoes(
        dados["historico"], bateria["capacidade_kwh"], bateria["reserva_inicial_kwh"])
    sem = sum(hora["deficit_nao_atendido_kwh"] for hora in simulacao)
    com = sum(hora["deficit_nao_atendido_kwh"] for hora in controle)
    print("\nCom o sistema reagindo, o consumo não atendido cai de {:.1f} kWh para {:.1f} kWh.".format(sem, com))


def etapa_previsao(dados):
    titulo("4. PREVISÃO DA GERAÇÃO EÓLICA (REGRESSÃO LINEAR)")
    resultado = mp.executar_previsao(dados["historico"], vento_ms=11)
    print("Equação da reta:", resultado["equacao"])
    print("R²: {:.3f} | EMA: {:.2f} kWh | ajuste {}".format(
        resultado["r2"], resultado["ema"], resultado["qualidade"]))
    print(resultado["mensagem"])


def main():
    dados = gd.gerar_dados(seed=SEED)
    series = etapa_dados(dados)
    simulacao = etapa_energia(dados, series)
    etapa_decisoes(dados, simulacao)
    etapa_previsao(dados)


if __name__ == "__main__":
    main()
