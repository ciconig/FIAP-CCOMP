"""Operações do help desk: consulta, filtro, fila de triagem, status e histórico.

Usa as mesmas constantes e o mesmo formato de histórico de dados.py, para que
as regras documentadas no README valham tanto na carga quanto no menu.
"""

from dados import CATEGORIAS, STATUS, TRANSICOES, dia_simulado
from visual import cor, erro, ok, status as cor_status

QTD_ULTIMAS = 5


def montar_fila(chamados):
    """Fila de triagem: chamados abertos na ordem em que foram registrados."""
    fila = []
    for chamado in chamados:
        if chamado["status"] == "aberto":
            fila.append(chamado)
    return fila


def listar_chamados(chamados):
    if not chamados:
        print("Nenhum chamado encontrado.")
        return
    print("\nPROTOCOLO | CATEGORIA | PRIORIDADE | BLOCO / ÁREA | STATUS")
    for chamado in chamados:
        prioridade = cor("URGENTE", "erro") if chamado["prioridade"] == "urgente" else chamado["prioridade"]
        print(f"{chamado['protocolo']} | {chamado['categoria']} | "
              f"{prioridade} | {chamado['bloco']} / {chamado['area']} | {cor_status(chamado['status'])}")


def _ler_dia(mensagem, minimo):
    """Pede um dia simulado inteiro, igual ou posterior ao mínimo informado."""
    while True:
        dia = dia_simulado(input(mensagem).strip())
        if dia is not None and dia >= minimo:
            return dia
        erro(f"Dia inválido. Informe um número inteiro a partir de {minimo}.")


def _ultimo_dia(chamado, historico):
    """Último dia conhecido do chamado: abertura ou evento mais recente."""
    dia = int(chamado["dia_abertura"])
    for evento in historico:
        if evento["protocolo"] == chamado["protocolo"]:
            dia = max(dia, int(evento["dia_evento"]))
    return dia


def _registrar(chamado, novo, dia, observacao, historico):
    """Aplica a mudança de status e empilha o evento no histórico."""
    historico.append({
        "protocolo": chamado["protocolo"],
        "dia_evento": str(dia),
        "status_anterior": chamado["status"],
        "status_novo": novo,
        "observacao": observacao,
    })
    chamado["status"] = novo
    if novo == "resolvido":
        chamado["dia_fechamento"] = str(dia)


def consultar_protocolo(por_protocolo):
    protocolo = input("Informe o protocolo (ex.: CH-001): ").strip().upper()
    chamado = por_protocolo.get(protocolo)
    if chamado is None:
        erro(f"Chamado {protocolo or '(vazio)'} não encontrado.")
        return None
    print("\n===== DADOS DO CHAMADO =====")
    for campo in ("protocolo", "categoria", "prioridade", "descricao", "bloco",
                  "area", "dia_abertura", "status", "dia_fechamento"):
        print(f"{campo}: {chamado[campo] or '-'}")
    return chamado


def filtrar_chamados(chamados):
    categoria = input(f"Categoria ({', '.join(CATEGORIAS)}; Enter para todas): ").strip().lower()
    status = input(f"Status ({', '.join(STATUS)}; Enter para todos): ").strip().lower()
    if (categoria and categoria not in CATEGORIAS) or (status and status not in STATUS):
        erro("Filtro inválido: use uma categoria e um status da lista.")
        return []

    encontrados = []
    for chamado in chamados:
        if (not categoria or chamado["categoria"] == categoria) and \
                (not status or chamado["status"] == status):
            encontrados.append(chamado)
    listar_chamados(encontrados)
    return encontrados


def atender_proximo_fila(fila_triagem, historico):
    """Retira o primeiro da fila (FIFO) e o coloca em atendimento."""
    if not fila_triagem:
        ok("Não há chamados na fila de triagem.")
        return None
    chamado = fila_triagem.pop(0)
    print(f"Próximo da fila: {chamado['protocolo']} — {chamado['descricao']} "
          f"({chamado['bloco']} / {chamado['area']}).")
    dia = _ler_dia("Dia do atendimento: ", _ultimo_dia(chamado, historico))
    _registrar(chamado, "em_atendimento", dia, "Chamado assumido na triagem.", historico)
    ok(f"Chamado {chamado['protocolo']} agora está em atendimento. "
          f"Restam {len(fila_triagem)} na fila.")
    return chamado


def atualizar_status(por_protocolo, fila_triagem, historico):
    protocolo = input("Informe o protocolo: ").strip().upper()
    chamado = por_protocolo.get(protocolo)
    if chamado is None:
        erro(f"Chamado {protocolo or '(vazio)'} não encontrado.")
        return None

    atual = chamado["status"]
    permitidos = TRANSICOES[atual]
    if not permitidos:
        erro(f"{protocolo} já está resolvido; o fluxo foi encerrado.")
        return None
    print(f"Status atual: {atual}. Próximos permitidos: {', '.join(permitidos)}.")
    novo = input("Novo status: ").strip().lower()
    if novo not in STATUS:
        erro("Status desconhecido. Use um dos valores da lista.")
        return None
    if novo not in permitidos:
        erro(f"Transição bloqueada: {atual} não pode ir direto para {novo}.")
        return None

    dia = _ler_dia("Dia da atualização: ", _ultimo_dia(chamado, historico))
    observacao = input("Observação (Enter para padrão): ").strip() or "Status atualizado."
    _registrar(chamado, novo, dia, observacao, historico)
    if chamado in fila_triagem:
        fila_triagem.remove(chamado)
    ok(f"Chamado {protocolo}: {atual} -> {novo} registrado no histórico.")
    return chamado


def exibir_ultimas_atualizacoes(historico):
    """Mostra o topo da pilha sem alterá-la: desempilha uma cópia."""
    if not historico:
        print("Não há atualizações registradas.")
        return
    pilha = historico.copy()
    print(f"\n===== ÚLTIMAS {min(QTD_ULTIMAS, len(pilha))} ATUALIZAÇÕES (mais recente primeiro) =====")
    for _ in range(min(QTD_ULTIMAS, len(pilha))):
        evento = pilha.pop()
        print(f"Dia {evento['dia_evento']} | {evento['protocolo']} | "
              f"{evento['status_anterior']} -> {evento['status_novo']} | {evento['observacao']}")
