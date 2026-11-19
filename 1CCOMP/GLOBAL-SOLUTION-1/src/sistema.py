from chamados import (
    atender_proximo_fila, atualizar_status, consultar_protocolo,
    exibir_ultimas_atualizacoes, filtrar_chamados, listar_chamados, montar_fila,
)
from dados import (
    CATEGORIAS, PRIORIDADES, carregar, carregar_historico, dia_simulado,
    salvar_novo_chamado,
)
from indicadores import exibir_painel_indicadores, exibir_visao_por_bloco
from painel_web import abrir_painel_web
from visual import erro, mostrar_banner, mostrar_menu, ok


def escolher(rotulo, opcoes):
    print(f"\n{rotulo}:")
    for numero, opcao in enumerate(opcoes, 1):
        print(f"  {numero} - {opcao}")
    while True:
        resposta = input("Escolha o número: ").strip()
        numero = dia_simulado(resposta)
        if numero is not None and 1 <= numero <= len(opcoes):
            return opcoes[numero - 1]
        erro("Opção inválida. Tente novamente.")


def texto_obrigatorio(rotulo):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if valor:
            return valor
        erro("Campo obrigatório. Tente novamente.")


def abrir_chamado(numeros):
    print("\nNovo chamado (não inclua nome ou apartamento do morador).")
    categoria = escolher("Categoria", CATEGORIAS)
    prioridade = escolher("Prioridade", PRIORIDADES)
    descricao = texto_obrigatorio("Descrição")
    bloco = texto_obrigatorio("Bloco")
    area = texto_obrigatorio("Área comum")
    while True:
        dia = input("Dia simulado de abertura (inteiro positivo): ").strip()
        if dia_simulado(dia) is not None:
            break
        erro("Dia inválido. Informe um número inteiro maior que zero.")
    numero = max(numeros, default=0) + 1
    chamado = {"protocolo": f"CH-{numero:03d}", "categoria": categoria,
                "prioridade": prioridade, "descricao": descricao, "bloco": bloco,
                "area": area, "dia_abertura": dia, "status": "aberto", "dia_fechamento": ""}
    chamado = salvar_novo_chamado(chamado)
    numeros.add(numero)
    ok(f"Chamado cadastrado! Protocolo: {chamado['protocolo']}")
    return chamado


def main():
    try:
        chamados, numeros = carregar()
        historico = carregar_historico(chamados)
    except (ValueError, OSError) as falha:
        erro(f"Erro ao carregar os dados iniciais: {falha}")
        return
    por_protocolo = {chamado["protocolo"]: chamado for chamado in chamados}
    fila_triagem = montar_fila(chamados)
    mostrar_banner(chamados, historico, fila_triagem)
    while True:
        mostrar_menu()
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            print("Encerrando a central de chamados. Até o próximo sol!")
            break
        try:
            if opcao == "1":
                listar_chamados(chamados)
            elif opcao == "2":
                novo = abrir_chamado(numeros)
                chamados.append(novo)
                por_protocolo[novo["protocolo"]] = novo
                fila_triagem.append(novo)
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
                exibir_painel_indicadores(chamados, historico)
            elif opcao == "9":
                exibir_visao_por_bloco(chamados, historico)
            elif opcao == "10":
                abrir_painel_web(chamados, historico)
            else:
                erro("Opção inválida. Tente novamente.")
        except (ValueError, OSError) as falha:
            erro(f"Erro ao acessar os dados: {falha}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado.")
