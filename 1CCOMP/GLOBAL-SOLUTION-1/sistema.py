# src/sistema.py
# Ponto de entrada da aplicação (Menu principal no terminal).

import os
import sys

# Garante que os módulos dentro de src/ sejam encontrados ao rodar `python src/sistema.py`
DIRETORIO_SRC = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_SRC not in sys.path:
    sys.path.insert(0, DIRETORIO_SRC)

from chamados import (
    abrir_chamado,
    atender_proximo_fila,
    atualizar_status,
    consultar_protocolo,
    exibir_ultimas_atualizacoes,
    filtrar_chamados,
    listar_chamados,
)

# Importa o módulo da Pessoa A se já estiver presente na pasta; caso contrário, usa dados de teste
try:
    from dados import carregar_dados
except ImportError:
    def carregar_dados():
        chamados_exemplo = [
            {
                "protocolo": "CH-001",
                "categoria": "acessibilidade",
                "prioridade": "urgente",
                "descricao": "Corrimão solto na rampa de acesso",
                "bloco": "Bloco A",
                "area": "Entrada social",
                "dia_abertura": 1,
                "status": "aberto",
                "dia_fechamento": None,
            },
            {
                "protocolo": "CH-002",
                "categoria": "iluminacao",
                "prioridade": "alta",
                "descricao": "Lâmpadas queimadas no subsolo",
                "bloco": "Bloco B",
                "area": "Garagem",
                "dia_abertura": 2,
                "status": "em_atendimento",
                "dia_fechamento": None,
            },
            {
                "protocolo": "CH-003",
                "categoria": "limpeza",
                "prioridade": "normal",
                "descricao": "Lixeira coletiva transbordando",
                "bloco": "Área Externa",
                "area": "Jardim",
                "dia_abertura": 3,
                "status": "resolvido",
                "dia_fechamento": 5,
            },
            {
                "protocolo": "CH-004",
                "categoria": "conservacao",
                "prioridade": "alta",
                "descricao": "Infiltração no teto do salão",
                "bloco": "Bloco C",
                "area": "Salão de festas",
                "dia_abertura": 4,
                "status": "aberto",
                "dia_fechamento": None,
            },
        ]
        por_protocolo = {c["protocolo"]: c for c in chamados_exemplo}
        fila_triagem = [c for c in chamados_exemplo if c["status"] == "aberto"]
        historico = [
            {
                "protocolo": "CH-002",
                "de": "aberto",
                "para": "em_atendimento",
                "dia": 3,
                "observacao": "Zelador iniciou verificação elétrica.",
            },
            {
                "protocolo": "CH-003",
                "de": "aberto",
                "para": "em_atendimento",
                "dia": 4,
                "observacao": "Equipe de limpeza acionada.",
            },
            {
                "protocolo": "CH-003",
                "de": "em_atendimento",
                "para": "resolvido",
                "dia": 5,
                "observacao": "Área higienizada e lixeira esvaziada.",
            },
        ]
        return chamados_exemplo, por_protocolo, fila_triagem, historico

# Importa o módulo da Pessoa C se já estiver presente na pasta
try:
    from indicadores import exibir_painel_indicadores, exibir_visao_por_bloco
except ImportError:
    def exibir_painel_indicadores(chamados):
        print("\n[AVISO] Módulo 'indicadores.py' (Pessoa C) ainda não foi integrado nesta pasta.")

    def exibir_visao_por_bloco(chamados):
        print("\n[AVISO] Módulo 'indicadores.py' (Pessoa C) ainda não foi integrado nesta pasta.")


def exibir_menu():
    print("\n========================================================")
    print("         HELP DESK DE CONDOMÍNIO - MENU PRINCIPAL       ")
    print("========================================================")
    print("1 Listar chamados          6 Atualizar status")
    print("2 Abrir chamado            7 Últimas atualizações")
    print("3 Consultar protocolo      8 Painel de indicadores")
    print("4 Filtrar                  9 Visão por bloco")
    print("5 Atender próximo da fila  0 Sair")
    print("========================================================")


def main():
    chamados, por_protocolo, fila_triagem, historico = carregar_dados()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_chamados(chamados)
        elif opcao == "2":
            abrir_chamado(chamados, por_protocolo, fila_triagem)
        elif opcao == "3":
            consultar_protocolo(por_protocolo)
        elif opcao == "4":
            filtrar_chamados(chamados)
        elif opcao == "5":
            atender_proximo_fila(fila_triagem, historico)
        elif opcao == "6":
            atualizar_status(por_protocolo, fila_triagem, historico)
        elif opcao == "7":
            exibir_ultimas_atualizacoes(historico)
        elif opcao == "8":
            exibir_painel_indicadores(chamados)
        elif opcao == "9":
            exibir_visao_por_bloco(chamados)
        elif opcao == "0":
            print("\nEncerrando o sistema do Help Desk. Até logo!")
            break
        else:
            print("\nOpção inválida! Digite um número de 0 a 9.")


if __name__ == "__main__":
    main()