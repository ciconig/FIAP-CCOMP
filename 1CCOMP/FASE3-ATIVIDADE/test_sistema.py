"""Testes do sistema da Fase 3 — apenas biblioteca padrão e asserts.
Execute a partir da pasta 1CCOMP/FASE3-ATIVIDADE:  python test_sistema.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "utils"))

import gerar_dados as gd       # noqa: E402
import decisoes as dc          # noqa: E402
import modelo_previsao as mp   # noqa: E402

# --- dados: mesma seed -> mesmos dados; estrutura e séries consistentes
a, b = gd.gerar_dados(seed=42), gd.gerar_dados(seed=42)
assert a["historico"] == b["historico"]
assert len(a["historico"]) == 24
assert a["estrutura"]["consumidores"]["essenciais"] == ["suporte_vida", "comunicacao"]
series = gd.extrair_series(a["historico"])
assert all(len(lista) == 24 for lista in series.values())
for r in a["historico"]:
    c = r["consumo"]
    assert c["total_kwh"] == c["suporte_vida_kwh"] + c["comunicacao_kwh"] + c["laboratorio_kwh"] + c["lazer_kwh"]

# --- análise de energia: exemplos do enunciado
assert dc.classificar_balanco(40, 70).startswith("RISCO")
assert dc.classificar_balanco(80, 30).startswith("SUGESTÃO")
assert dc.classificar_balanco(50, 50).startswith("EQUILÍBRIO")

# --- bateria: nunca passa da capacidade nem fica negativa
sim = dc.simular_bateria({"hora": [0, 1, 2], "geracao_kwh": [300, 0, 0], "consumo_kwh": [0, 150, 150]}, 200, 100)
assert [h["reserva_kwh"] for h in sim] == [200, 50, 0]
assert sim[0]["excedente_perdido_kwh"] == 200      # 100 + 300 - 200
assert sim[2]["deficit_nao_atendido_kwh"] == 100   # faltaram 100 kWh

# --- decisões: da regra mais grave para a mais branda
assert dc.decidir(20, 60, 30).startswith("ALERTA CRÍTICO")            # reserva baixa E consumo > geração
assert dc.decidir(60, 20, 30) == "ALERTA: reserva baixa - reduzir consumo"
assert dc.decidir(40, 70, 100) == "ALERTA: consumo alto e maior que a geração - reduzir consumo"
assert dc.decidir(10, 30, 100) == "ALERTA: consumo maior que geração"
assert dc.decidir(80, 30, 100) == "SUGESTÃO: armazenar energia excedente"
assert dc.decidir(50, 50, 100).startswith("EQUILÍBRIO")
# prioridade: suporte à vida e comunicação nunca são desligados
for decisao in ("ALERTA CRÍTICO: x", "ALERTA: x"):
    acoes = dc.acoes_por_decisao(decisao)
    assert "manter suporte_vida ligado" in acoes and "manter comunicacao ligado" in acoes
    assert not any(a.startswith("desligar suporte_vida") or a.startswith("desligar comunicacao") for a in acoes)

# --- sistema reagindo: corta não essenciais e não piora o consumo não atendido
controle = dc.simular_dia_com_decisoes(a["historico"], 200, 100)
base = dc.simular_bateria(series, 200, 100)
assert sum(h["deficit_nao_atendido_kwh"] for h in controle) <= sum(h["deficit_nao_atendido_kwh"] for h in base)

# --- previsão: exemplo literal do enunciado (vento 11 -> energia ≈ 27)
modelo = mp.ajustar_reta([8, 10, 12], [20, 25, 30])
assert abs(modelo["b1"] - 2.5) < 1e-9 and abs(modelo["b0"]) < 1e-9
assert abs(mp.prever(modelo, 11) - 27.5) < 1e-9
r = mp.executar_previsao(a["historico"], vento_ms=11)
assert 25 < r["eolica_prevista_kwh"] < 30 and r["qualidade"] == "Excelente"

print("Todos os testes passaram: dados, energia, bateria, decisões, prioridade e previsão.")
