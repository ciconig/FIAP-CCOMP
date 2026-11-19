import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import chamados
import dados


def base():
    lista, _ = dados.carregar(exibir_avisos=False)
    historico = dados.carregar_historico(lista)
    return lista, {c["protocolo"]: c for c in lista}, chamados.montar_fila(lista), historico


def rodar(funcao, respostas, *args):
    saida = io.StringIO()
    with patch("builtins.input", side_effect=respostas), redirect_stdout(saida):
        retorno = funcao(*args)
    return retorno, saida.getvalue()


class TestChamados(unittest.TestCase):
    def test_fila_respeita_ordem_de_registro(self):
        lista, _, fila, historico = base()
        self.assertEqual([c["protocolo"] for c in fila],
                         ["CH-005", "CH-006", "CH-011", "CH-012", "CH-014"])
        chamado, _ = rodar(chamados.atender_proximo_fila, ["3", "12"], fila, historico)
        self.assertEqual(chamado["protocolo"], "CH-005")
        self.assertEqual(chamado["status"], "em_atendimento")
        self.assertEqual(historico[-1]["dia_evento"], "12")

    def test_transicao_valida_registra_e_fecha(self):
        _, por_protocolo, fila, historico = base()
        tamanho = len(historico)
        chamado, saida = rodar(chamados.atualizar_status,
                               ["ch-002", "resolvido", "20", "Corrimão fixado"],
                               por_protocolo, fila, historico)
        self.assertEqual(chamado["status"], "resolvido")
        self.assertEqual(chamado["dia_fechamento"], "20")
        self.assertEqual(len(historico), tamanho + 1)
        self.assertEqual(historico[-1]["status_anterior"], "em_atendimento")
        self.assertIn("registrado no histórico", saida)

    def test_transicao_proibida_e_status_desconhecido(self):
        _, por_protocolo, fila, historico = base()
        tamanho = len(historico)
        _, saida = rodar(chamados.atualizar_status, ["CH-005", "resolvido"],
                         por_protocolo, fila, historico)
        self.assertIn("Transição bloqueada", saida)
        _, saida = rodar(chamados.atualizar_status, ["CH-005", "fechado"],
                         por_protocolo, fila, historico)
        self.assertIn("Status desconhecido", saida)
        _, saida = rodar(chamados.atualizar_status, ["CH-001"], por_protocolo, fila, historico)
        self.assertIn("já está resolvido", saida)
        self.assertEqual(len(historico), tamanho)
        self.assertEqual(por_protocolo["CH-005"]["status"], "aberto")

    def test_sair_de_aberto_remove_da_fila(self):
        _, por_protocolo, fila, historico = base()
        rodar(chamados.atualizar_status, ["CH-011", "em_atendimento", "15", ""],
              por_protocolo, fila, historico)
        self.assertNotIn(por_protocolo["CH-011"], fila)

    def test_consulta_e_filtro(self):
        lista, por_protocolo, _, _ = base()
        _, saida = rodar(chamados.consultar_protocolo, ["CH-099"], por_protocolo)
        self.assertIn("não encontrado", saida)
        encontrados, _ = rodar(chamados.filtrar_chamados, ["iluminacao", "aberto"], lista)
        self.assertEqual([c["protocolo"] for c in encontrados], ["CH-005", "CH-014"])
        encontrados, saida = rodar(chamados.filtrar_chamados, ["jardim", ""], lista)
        self.assertEqual(encontrados, [])
        self.assertIn("Filtro inválido", saida)

    def test_ultimas_atualizacoes_nao_altera_pilha(self):
        _, _, _, historico = base()
        copia = list(historico)
        _, saida = rodar(chamados.exibir_ultimas_atualizacoes, [], historico)
        self.assertEqual(historico, copia)
        self.assertIn("ÚLTIMAS 5", saida)


if __name__ == "__main__":
    unittest.main()
