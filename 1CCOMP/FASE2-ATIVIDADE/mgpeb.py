"""MGPEB — protótipo didático da atividade integradora (item 3).
Python 3, sem bibliotecas externas. Execute: python mgpeb.py
Os limites abaixo são hipóteses didáticas, não critérios reais de voo.
"""

COMBUSTIVEL_MINIMO = 50  # Referência de alerta adotada no cenário da equipe.
MASSA_MAXIMA = 12000    # Hipótese de capacidade da plataforma, em kg.


def cadastrar_modulo(modulos, codigo, nome, carga, prioridade,
                     combustivel, massa, criticidade):
    """Guarda um registro em uma lista; rejeita dados fora do domínio."""
    if buscar_por_codigo(modulos, codigo) is not None:
        return False
    if not (1 <= prioridade <= 5 and 0 <= combustivel <= 100 and massa > 0):
        return False
    modulos.append({
        "codigo": codigo, "nome": nome, "carga": carga,
        "prioridade": prioridade, "combustivel": combustivel,
        "massa": massa, "criticidade": criticidade,
        "impedimento": False  # Hipótese inicial: nenhum bloqueio individual.
    })
    return True


def buscar_por_codigo(modulos, codigo):
    """Busca linear: verifica cada registro, sem exigir ordenação."""
    for modulo in modulos:
        if modulo["codigo"] == codigo:
            return modulo
    return None


def buscar_menor_combustivel(modulos):
    """Busca linear do menor valor; em empate, mantém o primeiro."""
    if len(modulos) == 0:
        return None
    menor = modulos[0]
    for modulo in modulos[1:]:
        if modulo["combustivel"] < menor["combustivel"]:
            menor = modulo
    return menor


def buscar_maior_prioridade(modulos):
    """Prioridade 1 é a mais alta. Desempate: menor combustível."""
    if len(modulos) == 0:
        return None
    melhor = modulos[0]
    for modulo in modulos[1:]:
        if vem_antes(modulo, melhor):
            melhor = modulo
    return melhor


def buscar_por_carga(modulos, carga):
    """Busca linear; devolve todos os registros com a carga informada."""
    encontrados = []
    for modulo in modulos:
        if modulo["carga"].lower() == carga.lower():
            encontrados.append(modulo)
    return encontrados


def vem_antes(a, b):
    """Regra de fila: prioridade crescente, depois combustível crescente."""
    return (a["prioridade"] < b["prioridade"] or
            (a["prioridade"] == b["prioridade"] and
             a["combustivel"] < b["combustivel"]))


def ordenar_fila(fila):
    """Insertion Sort explícito, sem sorted() nem list.sort().
    Desloca os maiores para a direita. Empates exatos preservam a chegada.
    """
    for i in range(1, len(fila)):
        atual = fila[i]
        j = i - 1
        while j >= 0 and vem_antes(atual, fila[j]):
            fila[j + 1] = fila[j]
            j -= 1
        fila[j + 1] = atual


def decidir_pouso(modulo, area_livre, sistemas_ok):
    """IF/ELIF/ELSE e AND/OR/NOT implementam regras propostas.
    ALERTA impede pouso nesta simulação; não autoriza uma emergência real.
    """
    combustivel_ok = modulo["combustivel"] >= COMBUSTIVEL_MINIMO
    massa_ok = modulo["massa"] <= MASSA_MAXIMA
    impedimento = modulo["impedimento"]
    autorizado = (combustivel_ok and massa_ok and area_livre and
                  sistemas_ok and not impedimento)
    alerta = not combustivel_ok or impedimento

    if autorizado:
        return "AUTORIZADO"
    elif alerta:
        return "ALERTA"
    else:
        return "ESPERA"


def processar_rodada(fila, pousados, espera, pilha_alertas,
                     area_livre, sistemas_ok, exibir=True):
    """Fila: retirada pelo início. Pilha: alertas inseridos no topo.
    Cada autorização representa um pouso sequencial já concluído; não
    existem pousos simultâneos. Todos os módulos da rodada são avaliados.
    """
    while len(fila) > 0:
        modulo = fila.pop(0)  # Dequeue: primeiro da fila.
        decisao = decidir_pouso(modulo, area_livre, sistemas_ok)
        if decisao == "AUTORIZADO":
            pousados.append(modulo)
        elif decisao == "ALERTA":
            pilha_alertas.append(modulo)  # Push: topo da pilha.
        else:
            espera.append(modulo)
        if exibir:
            print(modulo["codigo"], modulo["nome"], "->", decisao)


def recolocar_espera(fila, espera):
    """Reavaliação explícita após corrigir condições; evita laço infinito."""
    while len(espera) > 0:
        fila.append(espera.pop(0))  # Enqueue: final da fila.
    ordenar_fila(fila)


def retirar_alerta(pilha_alertas):
    """Pop LIFO para atendimento manual, não para autorizar pouso.
    O chamador recebe o registro e deve tratá-lo; não o reinsere na fila.
    """
    if len(pilha_alertas) == 0:
        return None
    return pilha_alertas.pop()


def criar_modulos_equipe():
    """Dados fictícios já definidos na tarefa de cenário da equipe."""
    dados = [
        ("MD01", "Thor", "Energia", 1, 82, 8500, "Crítica"),
        ("MD02", "Asgard", "Habitação", 1, 75, 12000, "Crítica"),
        ("MD03", "Eir", "Medicina", 1, 48, 6200, "Crítica"),
        ("MD04", "Njord", "Água", 2, 68, 9300, "Alta"),
        ("MD05", "Idunn", "Oxigênio", 1, 90, 7800, "Crítica"),
        ("MD06", "Freyr", "Alimentos", 3, 72, 10500, "Média"),
        ("MD07", "Mimir", "Pesquisa", 4, 85, 5400, "Média"),
        ("MD08", "Sleipnir", "Suprimentos", 3, 60, 11200, "Alta"),
        ("MD09", "Heimdall", "Comunicação", 2, 78, 4800, "Alta"),
        ("MD10", "Brokkr", "Manutenção", 4, 42, 6900, "Média")
    ]
    modulos = []
    for dados_modulo in dados:
        cadastrar_modulo(modulos, *dados_modulo)
    return modulos


def mostrar_busca(rotulo, modulo):
    if modulo is None:
        print(rotulo, "nenhum módulo encontrado")
    else:
        print(rotulo, modulo["codigo"], modulo["nome"])


def executar_simulacao():
    modulos = criar_modulos_equipe()  # Lista: cadastro completo.
    fila = modulos[:]                # Cópia da sequência inicial MD01..MD10.
    pousados, espera, pilha_alertas = [], [], []
    mostrar_busca("Menor combustível:", buscar_menor_combustivel(modulos))
    mostrar_busca("Maior prioridade:", buscar_maior_prioridade(modulos))
    print("Carga Medicina:", [m["codigo"] for m in buscar_por_carga(modulos, "Medicina")])
    ordenar_fila(fila)
    print("Fila ordenada:", [m["codigo"] for m in fila])
    print("\nRodada: área livre e sistemas operacionais")
    processar_rodada(fila, pousados, espera, pilha_alertas, True, True)
    print("Pousados:", [m["codigo"] for m in pousados])
    print("Em espera:", [m["codigo"] for m in espera])
    print("Alertas (base -> topo):", [m["codigo"] for m in pilha_alertas])
    if len(pilha_alertas) > 0:
        print("Próximo alerta a tratar (LIFO):", pilha_alertas[-1]["codigo"])


if __name__ == "__main__":
    executar_simulacao()
