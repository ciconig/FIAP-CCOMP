"""Verificações da base e das regras de integridade, sem alterar os CSV originais."""

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import dados
import sistema


def chamado(**alteracoes):
    registro = {
        "protocolo": "CH-001", "categoria": "iluminacao", "prioridade": "alta",
        "descricao": "Lâmpada apagada", "bloco": "Bloco A", "area": "Garagem",
        "dia_abertura": "1", "status": "aberto", "dia_fechamento": "",
    }
    registro.update(alteracoes)
    return registro


def evento(dia, anterior, novo, protocolo="CH-001"):
    return {"protocolo": protocolo, "dia_evento": str(dia),
            "status_anterior": anterior, "status_novo": novo,
            "observacao": "Acompanhamento fictício"}


class TestDados(unittest.TestCase):
    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.pasta = Path(temporario.name)

    def escrever(self, nome, campos, registros):
        caminho = self.pasta / nome
        with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(registros)
        return caminho

    def test_base_entregue_cumpre_minimos_e_preserva_protocolo_rejeitado(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            chamados, numeros = dados.carregar()
        historico = dados.carregar_historico(chamados)
        self.assertGreaterEqual(len(chamados), 12)
        self.assertEqual({c["categoria"] for c in chamados}, set(dados.CATEGORIAS))
        self.assertGreaterEqual(len({c["status"] for c in chamados}), 3)
        self.assertGreaterEqual(len(historico), 8)
        self.assertIn("CH-013", saida.getvalue())
        self.assertIn("categoria", saida.getvalue())
        self.assertIn(13, numeros)
        self.assertNotIn("CH-013", [c["protocolo"] for c in chamados])
        dias = [int(e["dia_evento"]) for e in historico]
        self.assertEqual(dias, sorted(dias))

    def test_campos_obrigatorios_informam_o_nome(self):
        for campo in dados.OBRIGATORIOS:
            with self.subTest(campo=campo):
                erros = dados.validar(chamado(**{campo: "   "}))
                self.assertTrue(any(campo in erro for erro in erros))
        self.assertTrue(dados.validar(chamado(descricao=None)))

    def test_dominios_e_coerencia_dos_dias(self):
        invalidos = [
            {"categoria": "outros"}, {"prioridade": "baixa"}, {"status": "fechado"},
            {"protocolo": "CH-000"}, {"protocolo": "CH-١٢٣"},
            {"dia_abertura": "²"}, {"dia_abertura": "0"}, {"dia_abertura": "-1"},
            {"dia_abertura": "1.5"}, {"dia_abertura": "1" * 5000},
            {"dia_fechamento": "3"}, {"status": "resolvido"},
            {"status": "resolvido", "dia_abertura": "3", "dia_fechamento": "2"},
        ]
        for alteracoes in invalidos:
            with self.subTest(alteracoes=alteracoes):
                self.assertTrue(dados.validar(chamado(**alteracoes)))
        self.assertEqual(dados.validar(chamado(status="resolvido", dia_fechamento="1")), [])
        self.assertEqual(dados.validar(chamado()), [])

    def test_erros_estruturais_e_protocolos_duplicados_bloqueiam_carga(self):
        textos = [
            "protocolo,categoria\nCH-001,iluminacao\n",
            ",".join(dados.CAMPOS) + "\nCH-001,iluminacao\n",
            ",".join(dados.CAMPOS) + "\nCH-001,iluminacao,alta,luz,A,Hall,1,aberto,,extra\n",
            ",".join(dados.CAMPOS) + '\nCH-001,iluminacao,alta,"aspas sem fim\n',
        ]
        for texto in textos:
            with self.subTest(texto=texto):
                caminho = self.pasta / "malformado.csv"
                caminho.write_text(texto, encoding="utf-8")
                with self.assertRaises(ValueError):
                    dados.carregar(caminho)
        for registros in ([chamado(protocolo="errado")],
                          [chamado(categoria=""), chamado(protocolo="CH-0001")]):
            with self.subTest(registros=registros):
                caminho = self.escrever("duplicado.csv", dados.CAMPOS, registros)
                with self.assertRaises(ValueError):
                    dados.carregar(caminho, exibir_avisos=False)
        with self.assertRaisesRegex(ValueError, "não encontrado"):
            dados.carregar(self.pasta / "ausente.csv")

    def test_gravacao_preserva_invalido_e_csv_sem_quebra_final(self):
        caminho = self.escrever("chamados.csv", dados.CAMPOS,
                                [chamado(), chamado(protocolo="CH-002", categoria="")])
        caminho.write_bytes(caminho.read_bytes().rstrip(b"\r\n"))
        original = caminho.read_bytes()
        novo = chamado(protocolo="CH-003", descricao='Luz, "apagada"\nno hall')
        dados.salvar_novo_chamado(novo, caminho)
        self.assertTrue(caminho.read_bytes().startswith(original))
        chamados, numeros = dados.carregar(caminho, exibir_avisos=False)
        self.assertEqual(numeros, {1, 2, 3})
        self.assertEqual(chamados[-1], novo)
        salvo = caminho.read_bytes()
        for registro in (chamado(protocolo="CH-002"), chamado(categoria=""),
                         chamado(protocolo="CH-004", status="em_atendimento")):
            with self.subTest(registro=registro):
                with self.assertRaises(ValueError):
                    dados.salvar_novo_chamado(registro, caminho)
                self.assertEqual(caminho.read_bytes(), salvo)

    def test_historico_aceita_ciclo_com_terceiro_e_ordena_globalmente(self):
        chamados = [chamado(status="resolvido", dia_fechamento="5"),
                    chamado(protocolo="CH-002", status="em_atendimento")]
        eventos = [evento(2, "aberto", "em_atendimento"),
                   evento(3, "em_atendimento", "aguardando_terceiro"),
                   evento(4, "aguardando_terceiro", "em_atendimento"),
                   evento(5, "em_atendimento", "resolvido"),
                   evento(2, "aberto", "em_atendimento", "CH-002")]
        caminho = self.escrever("historico.csv", dados.CAMPOS_HISTORICO, eventos)
        resultado = dados.carregar_historico(chamados, caminho)
        self.assertEqual([int(e["dia_evento"]) for e in resultado], [2, 2, 3, 4, 5])
        self.assertEqual(resultado[-1]["status_novo"], "resolvido")

    def test_historico_rejeita_inconsistencias(self):
        resolvido = chamado(status="resolvido", dia_fechamento="3")
        corretos = [evento(2, "aberto", "em_atendimento"),
                    evento(3, "em_atendimento", "resolvido")]
        casos = [
            (resolvido, [evento(2, "aberto", "em_atendimento", "CH-099")]),
            (resolvido, [evento(2, "aberto", "desconhecido")]),
            (resolvido, [evento(0, "aberto", "em_atendimento")]),
            (resolvido, [evento(2, "aberto", "em_atendimento"), evento(1, "em_atendimento", "resolvido")]),
            (resolvido, [evento(2, "aberto", "resolvido")]),
            (resolvido, [evento(2, "em_atendimento", "resolvido")]),
            (resolvido, [evento(2, "aberto", "em_atendimento")]),
            (resolvido, []),
            (chamado(status="resolvido", dia_fechamento="4"), corretos),
            (resolvido, [dict(corretos[0], observacao=""), corretos[1]]),
        ]
        for registro, eventos in casos:
            with self.subTest(registro=registro, eventos=eventos):
                caminho = self.escrever("historico.csv", dados.CAMPOS_HISTORICO, eventos)
                with self.assertRaises(ValueError):
                    dados.carregar_historico([registro], caminho)
        vazio = self.escrever("historico.csv", dados.CAMPOS_HISTORICO, [])
        self.assertEqual(dados.carregar_historico([chamado()], vazio), [])

    def test_menu_cadastra_repetidamente_e_recupera_dados_do_disco(self):
        caminho = self.escrever("chamados.csv", dados.CAMPOS,
                                [chamado(), chamado(protocolo="CH-002", categoria="")])
        historico = self.escrever("historico.csv", dados.CAMPOS_HISTORICO, [])
        respostas = ["2", "²", "1", "2", "", "Luz apagada", "Bloco A", "Hall",
                     "²", "0", "3", "2", "3", "3", "Área suja", "Bloco B", "Piscina", "4", "1", "0"]
        saida = io.StringIO()
        with patch.object(sistema, "carregar", side_effect=lambda: dados.carregar(caminho)), \
                patch.object(sistema, "carregar_historico", side_effect=lambda c: dados.carregar_historico(c, historico)), \
                patch.object(sistema, "salvar_novo_chamado", side_effect=lambda c: dados.salvar_novo_chamado(c, caminho)), \
                patch("builtins.input", side_effect=respostas), redirect_stdout(saida):
            sistema.main()
        chamados, numeros = dados.carregar(caminho, exibir_avisos=False)
        self.assertEqual(numeros, {1, 2, 3, 4})
        self.assertEqual([c["protocolo"] for c in chamados], ["CH-001", "CH-003", "CH-004"])
        self.assertIn("Campo obrigatório", saida.getvalue())
        self.assertIn("Dia inválido", saida.getvalue())
        self.assertIn("CH-004 | limpeza", saida.getvalue())
        self.assertEqual(len(dados.carregar_historico(chamados, historico)), 0)


if __name__ == "__main__":
    unittest.main()
