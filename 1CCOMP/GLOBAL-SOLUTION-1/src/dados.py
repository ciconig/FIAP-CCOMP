"""Esquemas, leitura, validação e gravação dos dados fictícios do condomínio."""

import csv
import re
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent.parent / "data"
ARQUIVO = PASTA_DADOS / "chamados.csv"
ARQUIVO_HISTORICO = PASTA_DADOS / "historico.csv"

CAMPOS = ["protocolo", "categoria", "prioridade", "descricao", "bloco", "area",
          "dia_abertura", "status", "dia_fechamento"]
OBRIGATORIOS = CAMPOS[:-1]
CAMPOS_HISTORICO = ["protocolo", "dia_evento", "status_anterior", "status_novo",
                    "observacao"]
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
PRIORIDADES = ["urgente", "alta", "normal"]
STATUS = ["aberto", "em_atendimento", "aguardando_terceiro", "resolvido"]
PRAZOS = {"urgente": 1, "alta": 3, "normal": 7}
TRANSICOES = {
    "aberto": ["em_atendimento"],
    "em_atendimento": ["aguardando_terceiro", "resolvido"],
    "aguardando_terceiro": ["em_atendimento"],
    "resolvido": [],
}


def _texto(registro, campo):
    """Campos do contrato são strings; ausências e tipos indevidos ficam vazios."""
    valor = registro.get(campo, "")
    return valor.strip() if isinstance(valor, str) else ""


def dia_simulado(valor):
    """Converte texto com dígitos de 0 a 9 em dia positivo, ou retorna None."""
    if not isinstance(valor, str) or not re.fullmatch(r"[0-9]+", valor.strip()):
        return None
    try:
        dia = int(valor)
    except ValueError:
        return None
    return dia if dia > 0 else None


def _numero_protocolo(protocolo):
    if not re.fullmatch(r"CH-[0-9]{3,}", protocolo):
        return None
    try:
        numero = int(protocolo[3:])
    except ValueError:
        return None
    return numero if numero > 0 else None


def validar(chamado):
    """Retorna todos os erros do chamado, sem modificar o dicionário recebido."""
    dados = {campo: _texto(chamado, campo) for campo in CAMPOS}
    erros = []
    ausentes = [campo for campo in OBRIGATORIOS if not dados[campo]]
    if ausentes:
        erros.append("campos obrigatórios ausentes: " + ", ".join(ausentes))
    if _numero_protocolo(dados["protocolo"]) is None:
        erros.append("protocolo deve seguir CH-001, com número positivo e ao menos 3 dígitos")
    if dados["categoria"] not in CATEGORIAS:
        erros.append("categoria inválida; use " + ", ".join(CATEGORIAS))
    if dados["prioridade"] not in PRIORIDADES:
        erros.append("prioridade inválida; use " + ", ".join(PRIORIDADES))
    if dados["status"] not in STATUS:
        erros.append("status inválido; use " + ", ".join(STATUS))

    abertura = dia_simulado(dados["dia_abertura"])
    fechamento = dia_simulado(dados["dia_fechamento"])
    if abertura is None:
        erros.append("dia de abertura deve ser um inteiro positivo")
    if dados["status"] == "resolvido":
        if fechamento is None or (abertura is not None and fechamento < abertura):
            erros.append("resolvido precisa de dia de fechamento igual ou posterior à abertura")
    elif dados["dia_fechamento"]:
        erros.append("chamado não resolvido não pode ter dia de fechamento")
    return erros


def _ler_csv(caminho, campos):
    """Lê UTF-8 com ou sem BOM; problemas na estrutura bloqueiam a leitura."""
    caminho = Path(caminho)
    linhas = []
    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo, strict=True)
            if leitor.fieldnames != campos:
                raise ValueError(f"{caminho.name}: cabeçalho esperado: {','.join(campos)}")
            for linha in leitor:
                if None in linha or any(valor is None for valor in linha.values()):
                    raise ValueError(
                        f"{caminho.name}, linha {leitor.line_num}: quantidade de colunas incorreta."
                    )
                linhas.append((leitor.line_num, {
                    chave: valor.strip() for chave, valor in linha.items()
                }))
    except FileNotFoundError as erro:
        raise ValueError(f"Arquivo não encontrado: {caminho}. Mantenha data junto de src.") from erro
    except (UnicodeError, csv.Error) as erro:
        raise ValueError(f"{caminho.name}: CSV inválido ou fora da codificação UTF-8: {erro}") from erro
    return linhas


def carregar(caminho=ARQUIVO, exibir_avisos=True):
    """Retorna (lista de chamados válidos, conjunto de números reservados).

    Linhas com dados inválidos são avisadas e preservadas no CSV. Protocolos
    inválidos ou repetidos bloqueiam a carga para evitar reutilização de IDs.
    """
    validos = []
    numeros = set()
    for linha_num, linha in _ler_csv(caminho, CAMPOS):
        protocolo = linha["protocolo"]
        numero = _numero_protocolo(protocolo)
        if numero is None:
            raise ValueError(f"Linha {linha_num}: protocolo inválido; corrija o CSV antes de continuar.")
        if numero in numeros:
            raise ValueError(f"Linha {linha_num}: protocolo duplicado: {protocolo}.")
        numeros.add(numero)
        erros = validar(linha)
        if erros:
            if exibir_avisos:
                print(f"Aviso: linha {linha_num}, {protocolo} ignorado: {'; '.join(erros)}.")
        else:
            validos.append(linha)
    return validos, numeros


def carregar_historico(chamados, caminho=ARQUIVO_HISTORICO):
    """Valida as cadeias de status e retorna eventos do mais antigo ao recente.

    O arquivo pode agrupar eventos por protocolo, desde que a sequência de cada
    chamado esteja em ordem. O último item retornado será o topo da futura pilha.
    """
    por_protocolo = {chamado["protocolo"]: chamado for chamado in chamados}
    ultimos_status = {protocolo: "aberto" for protocolo in por_protocolo}
    ultimos_dias = {
        protocolo: int(chamado["dia_abertura"])
        for protocolo, chamado in por_protocolo.items()
    }
    eventos = []
    for linha_num, evento in _ler_csv(caminho, CAMPOS_HISTORICO):
        contexto = f"Histórico, linha {linha_num} ({evento['protocolo']})"
        ausentes = [campo for campo in CAMPOS_HISTORICO if not evento[campo]]
        if ausentes:
            raise ValueError(f"{contexto}: campos obrigatórios ausentes: {', '.join(ausentes)}.")
        protocolo = evento["protocolo"]
        if protocolo not in por_protocolo:
            raise ValueError(f"{contexto}: protocolo não encontrado entre os chamados válidos.")
        dia = dia_simulado(evento["dia_evento"])
        if dia is None or dia < ultimos_dias[protocolo]:
            raise ValueError(f"{contexto}: dia inválido, anterior à abertura ou ao evento anterior.")
        anterior = evento["status_anterior"]
        novo = evento["status_novo"]
        if anterior not in STATUS or novo not in STATUS:
            raise ValueError(f"{contexto}: status desconhecido.")
        if anterior != ultimos_status[protocolo] or novo not in TRANSICOES[anterior]:
            raise ValueError(f"{contexto}: transição inválida ou sequência de status interrompida.")
        ultimos_status[protocolo] = novo
        ultimos_dias[protocolo] = dia
        eventos.append(evento)

    for protocolo, chamado in por_protocolo.items():
        if ultimos_status[protocolo] != chamado["status"]:
            raise ValueError(f"Histórico de {protocolo}: último status difere do CSV de chamados.")
        if chamado["status"] == "resolvido" and ultimos_dias[protocolo] != int(chamado["dia_fechamento"]):
            raise ValueError(f"Histórico de {protocolo}: dia da resolução difere do fechamento.")
    return sorted(eventos, key=lambda evento: int(evento["dia_evento"]))


def salvar_novo_chamado(chamado, caminho=ARQUIVO):
    """Acrescenta um chamado aberto, sem reescrever nem apagar linhas rejeitadas."""
    dados = {campo: _texto(chamado, campo) for campo in CAMPOS}
    erros = validar(dados)
    if dados["status"] != "aberto":
        erros.append("um novo chamado deve começar com status aberto")
    if erros:
        raise ValueError("Cadastro não realizado: " + "; ".join(erros))
    _, numeros = carregar(caminho, exibir_avisos=False)
    if _numero_protocolo(dados["protocolo"]) in numeros:
        raise ValueError("Cadastro não realizado: protocolo já reservado no CSV.")

    # Evita juntar o novo registro ao anterior em CSV sem quebra de linha final.
    caminho = Path(caminho)
    with caminho.open("rb") as arquivo:
        arquivo.seek(-1, 2)
        precisa_quebra = arquivo.read(1) not in (b"\n", b"\r")
    with caminho.open("a", encoding="utf-8", newline="") as arquivo:
        if precisa_quebra:
            arquivo.write("\n")
        csv.DictWriter(arquivo, fieldnames=CAMPOS).writerow(dados)
    return dados
