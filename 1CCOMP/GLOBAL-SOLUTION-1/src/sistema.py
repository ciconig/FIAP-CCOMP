"""Cadastro simples de chamados de áreas comuns, usando apenas Python padrão."""
from dados import (
    CATEGORIAS, PRIORIDADES, carregar, carregar_historico, dia_simulado,
    salvar_novo_chamado,
)


def escolher(rotulo, opcoes):
    print(f"\n{rotulo}:")
    for numero, opcao in enumerate(opcoes, 1):
        print(f"  {numero} - {opcao}")
    while True:
        resposta = input("Escolha o número: ").strip()
        numero = dia_simulado(resposta)
        if numero is not None and 1 <= numero <= len(opcoes):
            return opcoes[numero - 1]
        print("Opção inválida. Tente novamente.")


def texto_obrigatorio(rotulo):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if valor:
            return valor
        print("Campo obrigatório. Tente novamente.")


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
        print("Dia inválido. Informe um número inteiro maior que zero.")
    numero = max(numeros, default=0) + 1
    chamado = {"protocolo": f"CH-{numero:03d}", "categoria": categoria,
                "prioridade": prioridade, "descricao": descricao, "bloco": bloco,
                "area": area, "dia_abertura": dia, "status": "aberto", "dia_fechamento": ""}
    chamado = salvar_novo_chamado(chamado)
    numeros.add(numero)
    print(f"Chamado cadastrado! Protocolo: {chamado['protocolo']}")
    return chamado


def listar(chamados):
    if not chamados:
        print("Nenhum chamado válido cadastrado.")
        return
    print("\nPROTOCOLO | CATEGORIA | PRIORIDADE | BLOCO / ÁREA | STATUS")
    for chamado in chamados:
        prioridade = chamado["prioridade"].upper() if chamado["prioridade"] == "urgente" else chamado["prioridade"]
        print(f"{chamado['protocolo']} | {chamado['categoria']} | "
              f"{prioridade} | {chamado['bloco']} / {chamado['area']} | {chamado['status']}")


def main():
    try:
        chamados, numeros = carregar()
        historico = carregar_historico(chamados)
    except (ValueError, OSError) as erro:
        print(f"Erro ao carregar os dados iniciais: {erro}")
        return
    print(f"Base carregada: {len(chamados)} chamados válidos e {len(historico)} eventos de histórico.")
    while True:
        print("\n=== HELP DESK DO CONDOMÍNIO ===")
        print("1 - Listar chamados\n2 - Abrir chamado\n0 - Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            print("Até logo!")
            break
        elif opcao == "1" or opcao == "2":
            try:
                if opcao == "1":
                    listar(chamados)
                else:
                    novo = abrir_chamado(numeros)
                    chamados.append(novo)
            except (ValueError, OSError) as erro:
                print(f"Erro ao acessar os dados: {erro}")
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado.")
