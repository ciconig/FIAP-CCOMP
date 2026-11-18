7
8
9
0
"""Operacoes relacionadas aos chamados do help desk."""


CATEGORIAS_VALIDAS = (
    "acessibilidade",
    "iluminacao",
    "limpeza",
    "conservacao",
)
PRIORIDADES_VALIDAS = ("urgente", "alta", "normal", "baixa")
STATUS_VALIDOS = (
    "aberto",
    "em_atendimento",
    "aguardando_terceiro",
    "resolvido",
)
TRANSICOES_VALIDAS = {
    "aberto": {"em_atendimento", "aguardando_terceiro"},
    "em_atendimento": {"aguardando_terceiro", "resolvido"},
    "aguardando_terceiro": {"em_atendimento", "resolvido"},
    "resolvido": set(),
}


def _ler_inteiro(mensagem):
    while True:
        valor = input(mensagem).strip()
        try:
            return int(valor)
        except ValueError:
            print("Informe um numero inteiro valido.")


def _encontrar_chamado(por_protocolo, protocolo):
    return por_protocolo.get(protocolo.strip().upper())


def listar_chamados(chamados):
    if not chamados:
        print("\nNenhum chamado cadastrado.")
        return

    print("\n===== LISTA DE CHAMADOS =====")
    for chamado in chamados:
        print(
            f"{chamado['protocolo']} | {chamado['categoria']} | "
            f"{chamado['prioridade']} | {chamado['status']} | "
            f"{chamado['bloco']} - {chamado['area']} "
        )
        print(f"  Descricao: {chamado['descricao']}")


def abrir_chamado(chamados, por_protocolo, fila_triagem):
    categoria = input("Categoria: ").strip().lower()
    prioridade = input("Prioridade (urgente/alta/normal/baixa): ").strip().lower()
    descricao = input("Descricao do problema: ").strip()
    bloco = input("Bloco: ").strip()
    area = input("Area: ").strip()

    if not all((categoria, prioridade, descricao, bloco, area)):
        print("\nErro: todos os dados do chamado sao obrigatorios.")
        return None

    if categoria not in CATEGORIAS_VALIDAS:
        print("\nErro: categoria inexistente.")
        return None

    if prioridade not in PRIORIDADES_VALIDAS:
        print("\nErro: prioridade invalida.")
        return None

    dia_abertura = _ler_inteiro("Dia da abertura: ")

    numeros = []
    for chamado in chamados:
        protocolo = chamado.get("protocolo", "")
        if protocolo.startswith("CH-"):
            try:
                numeros.append(int(protocolo[3:]))
            except ValueError:
                pass

    protocolo = f"CH-{max(numeros, default=0) + 1:03d}"
    chamado = {
        "protocolo": protocolo,
        "categoria": categoria,
        "prioridade": prioridade,
        "descricao": descricao,
        "bloco": bloco,
        "area": area,
        "dia_abertura": dia_abertura,
        "status": "aberto",
        "dia_fechamento": None,
    }

    chamados.append(chamado)
    por_protocolo[protocolo] = chamado
    fila_triagem.append(chamado)

    print(f"\nChamado aberto com sucesso! Protocolo: {protocolo}")
    return chamado


def consultar_protocolo(por_protocolo):
    protocolo = input("Informe o protocolo (ex.: CH-001): ").strip().upper()
    chamado = _encontrar_chamado(por_protocolo, protocolo)

    if chamado is None:
        print("\nChamado nao encontrado.")
        return None

    print("\n===== DADOS DO CHAMADO =====")
    for campo in (
        "protocolo",
        "categoria",
        "prioridade",
        "descricao",
        "bloco",
        "area",
        "dia_abertura",
        "status",
        "dia_fechamento",
    ):
        print(f"{campo}: {chamado.get(campo)}")
    return chamado


def filtrar_chamados(chamados):
    categoria = input("Categoria (Enter para ignorar): ").strip().lower()
    status = input("Status (Enter para ignorar): ").strip().lower()

    encontrados = []
    for chamado in chamados:
        if categoria and chamado.get("categoria", "").lower() != categoria:
            continue
        if status and chamado.get("status", "").lower() != status:
            continue
        encontrados.append(chamado)

    if not encontrados:
        print("\nNenhum chamado corresponde ao filtro.")
        return encontrados

    listar_chamados(encontrados)
    return encontrados


def atender_proximo_fila(fila_triagem, historico):
    if not fila_triagem:
        print("\nNao existem chamados na fila de triagem.")
        return None

    chamado = fila_triagem.pop(0)
    chamado["status"] = "em_atendimento"
    dia = _ler_inteiro("Dia do atendimento: ")

    historico.append(
        {
            "protocolo": chamado["protocolo"],
            "de": "aberto",
            "para": "em_atendimento",
            "dia": dia,
            "observacao": "Chamado iniciado.",
        }
    )

    print(f"\nChamado {chamado['protocolo']} foi enviado para atendimento.")
    return chamado


def atualizar_status(por_protocolo, fila_triagem, historico):
    protocolo = input("Informe o protocolo: ").strip().upper()
    chamado = _encontrar_chamado(por_protocolo, protocolo)

    if chamado is None:
        print("\nChamado nao encontrado.")
        return None

    novo_status = input(
        "Novo status (aberto/em_atendimento/aguardando_terceiro/resolvido): "
    ).strip().lower()
    if novo_status not in STATUS_VALIDOS:
        print("\nStatus invalido.")
        return None

    status_anterior = chamado["status"]
    if novo_status == status_anterior:
        print("\nO chamado ja esta nesse status.")
        return chamado

    if novo_status not in TRANSICOES_VALIDAS.get(status_anterior, set()):
        print(
            f"\nTransicao bloqueada: nao e permitido alterar "
            f"{status_anterior} diretamente para {novo_status}."
        )
        return None

    chamado["status"] = novo_status
    dia = _ler_inteiro("Dia da atualizacao: ")
    observacao = input("Observacao: ").strip()

    if novo_status == "resolvido":
        chamado["dia_fechamento"] = dia
    elif novo_status == "aberto":
        chamado["dia_fechamento"] = None

    if chamado not in fila_triagem and novo_status == "aberto":
        fila_triagem.append(chamado)
    elif novo_status != "aberto":
        while chamado in fila_triagem:
            fila_triagem.remove(chamado)

    historico.append(
        {
            "protocolo": chamado["protocolo"],
            "de": status_anterior,
            "para": novo_status,
            "dia": dia,
            "observacao": observacao or "Status atualizado.",
        }
    )
    print(f"\nStatus do chamado {protocolo} atualizado.")
    return chamado


def exibir_ultimas_atualizacoes(historico):
    if not historico:
        print("\nNao existem atualizacoes registradas.")
        return

    print("\n===== ULTIMAS ATUALIZACOES =====")
    for atualizacao in reversed(historico[-5:]):
        print(
            f"Dia {atualizacao['dia']} | {atualizacao['protocolo']} | "
            f"{atualizacao['de']} -> {atualizacao['para']} | "
            f"{atualizacao['observacao']}"
        )
