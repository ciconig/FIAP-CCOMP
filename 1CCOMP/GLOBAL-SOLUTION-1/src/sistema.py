"""Cadastro simples de chamados de áreas comuns, usando apenas Python padrão."""
import csv
import re
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "data" / "chamados.csv"
CAMPOS = ["protocolo", "categoria", "prioridade", "descricao", "bloco", "area",
          "dia_abertura", "status", "dia_fechamento"]
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
PRIORIDADES = ["urgente", "alta", "normal"]
STATUS = ["aberto", "em_atendimento", "aguardando_terceiro", "resolvido"]


def validar(chamado):
    """Retorna os motivos pelos quais uma linha não pode ser usada."""
    erros = []
    obrigatorios = CAMPOS[:-1]
    if any(not chamado.get(campo, "").strip() for campo in obrigatorios):
        erros.append("há campo obrigatório vazio")
    if not re.fullmatch(r"CH-\d{3,}", chamado.get("protocolo", "")):
        erros.append("protocolo inválido")
    if chamado.get("categoria") not in CATEGORIAS:
        erros.append("categoria inválida ou ausente")
    if chamado.get("prioridade") not in PRIORIDADES:
        erros.append("prioridade inválida")
    if chamado.get("status") not in STATUS:
        erros.append("status inválido")
    abertura = chamado.get("dia_abertura", "")
    fechamento = chamado.get("dia_fechamento", "")
    if not abertura.isdigit() or int(abertura) < 1:
        erros.append("dia de abertura deve ser um inteiro positivo")
    elif chamado.get("status") == "resolvido":
        if not fechamento.isdigit() or int(fechamento) < int(abertura):
            erros.append("resolvido precisa de dia de fechamento igual ou posterior à abertura")
    elif fechamento:
        erros.append("chamado não resolvido não pode ter dia de fechamento")
    return erros


def carregar():
    """Lê todas as linhas, separa válidas e reserva os protocolos inválidos também."""
    validos = []
    numeros = set()
    try:
        with ARQUIVO.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            if leitor.fieldnames != CAMPOS:
                raise ValueError("O cabeçalho do CSV não corresponde ao esquema esperado.")
            for linha_num, linha in enumerate(leitor, start=2):
                if None in linha or any(valor is None for valor in linha.values()):
                    raise ValueError(f"Linha {linha_num}: quantidade de colunas incorreta.")
                linha = {chave: valor.strip() for chave, valor in linha.items()}
                protocolo = linha["protocolo"]
                if not re.fullmatch(r"CH-\d{3,}", protocolo):
                    raise ValueError(f"Linha {linha_num}: protocolo inválido; corrija o CSV antes de continuar.")
                numero = int(protocolo[3:])
                if numero in numeros:
                    raise ValueError(f"Linha {linha_num}: protocolo duplicado; corrija o CSV antes de continuar.")
                numeros.add(numero)
                erros = validar(linha)
                if erros:
                    print(f"Aviso: {protocolo} ignorado na listagem: {', '.join(erros)}.")
                else:
                    validos.append(linha)
    except FileNotFoundError:
        raise ValueError(f"Arquivo não encontrado: {ARQUIVO}. Mantenha a pasta data junto de src.")
    return validos, numeros


def escolher(rotulo, opcoes):
    print(f"\n{rotulo}:")
    for numero, opcao in enumerate(opcoes, 1):
        print(f"  {numero} - {opcao}")
    while True:
        resposta = input("Escolha o número: ").strip()
        if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
            return opcoes[int(resposta) - 1]
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
        if dia.isdigit() and int(dia) > 0:
            break
        print("Dia inválido. Informe um número inteiro maior que zero.")
    numero = max(numeros, default=0) + 1
    chamado = {"protocolo": f"CH-{numero:03d}", "categoria": categoria,
                "prioridade": prioridade, "descricao": descricao, "bloco": bloco,
                "area": area, "dia_abertura": dia, "status": "aberto", "dia_fechamento": ""}
    erros = validar(chamado)
    if erros:
        print("Cadastro não realizado: " + ", ".join(erros))
        return
    with ARQUIVO.open("a", encoding="utf-8", newline="") as arquivo:
        csv.DictWriter(arquivo, fieldnames=CAMPOS).writerow(chamado)
    print(f"Chamado cadastrado! Protocolo: {chamado['protocolo']}")


def listar(chamados):
    if not chamados:
        print("Nenhum chamado válido cadastrado.")
        return
    print("\nPROTOCOLO | CATEGORIA | BLOCO / ÁREA | STATUS")
    for chamado in chamados:
        print(f"{chamado['protocolo']} | {chamado['categoria']} | "
              f"{chamado['bloco']} / {chamado['area']} | {chamado['status']}")


def main():
    while True:
        print("\n=== HELP DESK DO CONDOMÍNIO ===")
        print("1 - Listar chamados\n2 - Abrir chamado\n0 - Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            print("Até logo!")
            break
        elif opcao == "1" or opcao == "2":
            try:
                chamados, numeros = carregar()
                if opcao == "1":
                    listar(chamados)
                else:
                    abrir_chamado(numeros)
            except (ValueError, OSError, csv.Error) as erro:
                print(f"Erro ao acessar os dados: {erro}")
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado.")
