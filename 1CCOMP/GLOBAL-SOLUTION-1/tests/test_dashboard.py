"""Verificações do dashboard: contagens, matrizes, hierarquia, indicadores e menu."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import dados
import dashboard
import indicadores


def chamado(protocolo, categoria, prioridade, bloco, abertura, status, fechamento=""):
    return {"protocolo": protocolo, "categoria": categoria, "prioridade": prioridade,
            "descricao": "Teste", "bloco": bloco, "area": "Hall",
            "dia_abertura": str(abertura), "status": status,
            "dia_fechamento": str(fechamento)}


AMOSTRA = [
    chamado("CH-001", "iluminacao", "alta", "Bloco A", 1, "resolvido", 3),
    chamado("CH-002", "limpeza", "urgente", "bloco  a", 2, "aberto"),
    chamado("CH-003", "limpeza", "normal", "Bloco B", 4, "em_atendimento"),
]
EVENTOS = [
    {"protocolo": "CH-001", "dia_evento": "2", "status_anterior": "aberto",
     "status_novo": "em_atendimento", "observacao": "Início"},
    {"protocolo": "CH-001", "dia_evento": "3", "status_anterior": "em_atendimento",
     "status_novo": "resolvido", "observacao": "Fim"},
    {"protocolo": "CH-003", "dia_evento": "5", "status_anterior": "aberto",
     "status_novo": "em_atendimento", "observacao": "Equipe acionada"},
]


class TestDashboard(unittest.TestCase):
    def test_contagens_e_matrizes(self):
        contagem = dashboard.contar_por(AMOSTRA, "categoria", dados.CATEGORIAS)
        self.assertEqual(contagem, {"iluminacao": 1, "acessibilidade": 0,
                                    "limpeza": 2, "conservacao": 0})
        matriz = dashboard.matriz_categoria_status(AMOSTRA)
        self.assertEqual(len(matriz), len(dados.CATEGORIAS))
        self.assertEqual(matriz[2], [1, 1, 0, 0])  # limpeza: 1 aberto, 1 em atendimento
        blocos = dashboard.blocos_disponiveis(AMOSTRA)
        self.assertEqual(blocos, ["Bloco A", "Bloco B"])  # "bloco  a" é agrupado em Bloco A
        self.assertEqual(dashboard.matriz_bloco_status(AMOSTRA, blocos),
                         [[1, 0, 0, 1], [0, 1, 0, 0]])

    def test_hierarquia_bloco_categoria_chamados(self):
        hierarquia = dashboard.montar_hierarquia(AMOSTRA)
        self.assertEqual(list(hierarquia), ["Bloco A", "Bloco B"])
        self.assertEqual([c["protocolo"] for c in hierarquia["Bloco A"]["limpeza"]], ["CH-002"])
        self.assertNotIn("conservacao", hierarquia["Bloco A"])

    def test_indicadores(self):
        ind = dashboard.calcular_indicadores(AMOSTRA, EVENTOS)
        self.assertEqual(ind["referencia"], 5)
        self.assertEqual((ind["total"], ind["resolvidos"], ind["pendentes"]), (3, 1, 2))
        self.assertAlmostEqual(ind["taxa_resolucao"], 100 / 3)
        self.assertEqual(ind["tempo_medio_resolucao"], 2)
        self.assertEqual(ind["resolvidos_no_prazo"], 1)
        self.assertEqual(ind["espera_media_pendentes"], (3 + 1) / 2)
        # CH-002 urgente espera 3 > 1 (atrasado); CH-003 normal espera 1 <= 7.
        self.assertEqual([c["protocolo"] for c in ind["atrasados"]], ["CH-002"])
        self.assertEqual(ind["criticos_atrasados"], 1)

    def test_pilha_nao_altera_historico(self):
        recentes = dashboard.ultimos_eventos(EVENTOS, 2)
        self.assertEqual([e["dia_evento"] for e in recentes], ["5", "3"])
        self.assertEqual(len(EVENTOS), 3)

    def test_base_vazia_nao_quebra(self):
        self.assertEqual(dashboard.percentual(1, 0), 0.0)
        ind = dashboard.calcular_indicadores([], [])
        self.assertIsNone(ind["tempo_medio_resolucao"])
        self.assertIsNone(ind["espera_media_pendentes"])
        saida = io.StringIO()
        with redirect_stdout(saida):
            dashboard.exibir_dashboard([], [])
            dashboard.exibir_painel_bloco([], [], "Bloco Z")
        self.assertIn("Nenhum chamado", saida.getvalue())

    def test_base_entregue_fecha_os_totais(self):
        with redirect_stdout(io.StringIO()):
            chamados, _ = dados.carregar()
        historico = dados.carregar_historico(chamados)
        for matriz in (dashboard.matriz_categoria_status(chamados),
                       dashboard.matriz_bloco_status(chamados,
                                                     dashboard.blocos_disponiveis(chamados))):
            self.assertEqual(sum(sum(linha) for linha in matriz), len(chamados))
        ind = dashboard.calcular_indicadores(chamados, historico)
        self.assertEqual(ind["resolvidos"] + ind["pendentes"], len(chamados))
        saida = io.StringIO()
        with redirect_stdout(saida):
            dashboard.exibir_dashboard(chamados, historico)
        texto = saida.getvalue()
        self.assertIn("MATRIZ BLOCO/TORRE X STATUS", texto)
        self.assertIn("CONCLUSÃO", texto)
        self.assertNotIn("CH-013", texto)  # registro inválido fica fora do painel

    def test_opcoes_8_e_9_do_menu(self):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=["7", "x", "2"]), redirect_stdout(saida):
            indicadores.exibir_painel_indicadores(AMOSTRA)
            indicadores.exibir_visao_por_bloco(AMOSTRA, EVENTOS)
        texto = saida.getvalue()
        self.assertIn("DASHBOARD DE CHAMADOS", texto)
        self.assertIn("Opção inválida", texto)
        self.assertIn("PAINEL DO BLOCO B", texto)
        self.assertIn("Equipe acionada", texto)  # evento do Bloco B no topo da pilha

    def test_aceita_formato_do_modulo_de_chamados(self):
        # Dias como inteiro/None, prioridade sem prazo e eventos com de/para/dia.
        base = [dict(AMOSTRA[0], dia_abertura=1, dia_fechamento=3),
                dict(AMOSTRA[1], prioridade="baixa", dia_abertura=2, dia_fechamento=None)]
        eventos = [{"protocolo": "CH-001", "de": "em_atendimento", "para": "resolvido",
                    "dia": 6, "observacao": "Fim"}]
        ind = dashboard.calcular_indicadores(base, eventos)
        self.assertEqual(ind["referencia"], 6)
        self.assertEqual(ind["atrasados"], [])  # "baixa" não tem prazo definido
        with redirect_stdout(io.StringIO()) as saida:
            dashboard.exibir_dashboard(base, eventos)
        self.assertIn("Em atendimento -> Resolvido", saida.getvalue())

if __name__ == "__main__":
    unittest.main()
