"""Ponte entre o menu principal (opções 8 e 9) e o dashboard da parte C.

O sistema.py do grupo chama exibir_painel_indicadores(chamados) e
exibir_visao_por_bloco(chamados). O histórico é opcional: quando o menu o
envia, o painel também mostra as últimas atualizações (pilha).
"""

from dashboard import blocos_disponiveis, exibir_dashboard, exibir_painel_bloco


def exibir_painel_indicadores(chamados, historico=None):
    """Opção 8: painel geral com todos os blocos/torres."""
    if historico is None:
        historico = []
    exibir_dashboard(chamados, historico)


def escolher_bloco(blocos):
    """Mostra os blocos numerados e repete a pergunta até a escolha ser válida."""
    print("\nBlocos/torres disponíveis:")
    for numero, bloco in enumerate(blocos, 1):
        print(f"  {numero} - {bloco}")
    while True:
        resposta = input("Escolha o número do bloco: ").strip()
        if resposta.isdigit() and 1 <= int(resposta) <= len(blocos):
            return blocos[int(resposta) - 1]
        print("Opção inválida. Tente novamente.")


def exibir_visao_por_bloco(chamados, historico=None):
    """Opção 9: painel de um único bloco/torre escolhido pelo usuário."""
    if historico is None:
        historico = []
    blocos = blocos_disponiveis(chamados)
    if not blocos:
        print("\nNenhum bloco com chamados cadastrados.")
        return
    exibir_painel_bloco(chamados, historico, escolher_bloco(blocos))
