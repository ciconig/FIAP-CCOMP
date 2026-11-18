"""Dashboard textual dos chamados: indicadores, matrizes e hierarquia por bloco.

Neste condomínio, cada bloco corresponde a uma torre. O módulo só lê os dados
já validados por dados.py; não altera os CSV. Os cálculos ficam separados da
exibição para que possam ser testados sem depender do terminal.
"""

try:
    from dados import CATEGORIAS, PRAZOS, STATUS
except ImportError:
    # Permite usar o painel mesmo se dados.py não estiver na mesma pasta.
    CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
    STATUS = ["aberto", "em_atendimento", "aguardando_terceiro", "resolvido"]
    PRAZOS = {"urgente": 1, "alta": 3, "normal": 7}

ROTULOS_CATEGORIA = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação",
}
ROTULOS_STATUS = {
    "aberto": "Aberto",
    "em_atendimento": "Em atendimento",
    "aguardando_terceiro": "Aguardando terceiro",
    "resolvido": "Resolvido",
}
# Cabeçalhos curtos para as colunas das matrizes (legenda exibida abaixo delas).
COLUNAS_STATUS = ["Aberto", "Em atend.", "Ag. terc.", "Resolv."]
LARGURA_BARRA = 20
LINHA = "=" * 72
SEPARADOR = "-" * 72


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def nome_bloco(chamado):
    """Padroniza o bloco para agrupar 'bloco a' e 'Bloco  A' no mesmo grupo."""
    return " ".join(chamado["bloco"].split()).title()


def percentual(parte, total):
    """Proporção em %, com proteção contra divisão por zero."""
    if total == 0:
        return 0.0
    return parte * 100 / total


def barra(valor, maximo):
    """Barra de texto proporcional ao maior valor da tabela."""
    if maximo == 0 or valor == 0:
        return ""
    tamanho = round(valor * LARGURA_BARRA / maximo)
    if tamanho == 0:
        tamanho = 1  # um valor positivo nunca fica invisível
    return "#" * tamanho


def converter_dia(valor):
    """Aceita dia como texto ("3"), inteiro (3) ou vazio ("" / None)."""
    if valor is None or valor == "":
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def prazo_de(chamado):
    """Prazo em dias da prioridade; None se a prioridade não tiver prazo definido."""
    return PRAZOS.get(chamado.get("prioridade"))


def dados_evento(evento):
    """Lê eventos nos dois formatos do grupo: (dia_evento, status_anterior,
    status_novo) de historico.csv ou (dia, de, para) do módulo de chamados."""
    dia = evento.get("dia_evento", evento.get("dia"))
    anterior = evento.get("status_anterior", evento.get("de", ""))
    novo = evento.get("status_novo", evento.get("para", ""))
    return converter_dia(dia), anterior, novo


def rotulo_status(status):
    return ROTULOS_STATUS.get(status, status)


def eh_pendente(chamado):
    return not chamado["status"] == "resolvido"


def dia_referencia(chamados, historico):
    """Dia simulado "de hoje": o maior dia que aparece na base."""
    maior = 0
    for chamado in chamados:
        dias = [converter_dia(chamado.get("dia_abertura")),
                converter_dia(chamado.get("dia_fechamento"))]
        for dia in dias:
            if dia is not None and dia > maior:
                maior = dia
    for evento in historico:
        dia, _, _ = dados_evento(evento)
        if dia is not None and dia > maior:
            maior = dia
    return maior


def blocos_disponiveis(chamados):
    """Lista ordenada e sem repetição dos blocos (torres) com chamados."""
    blocos = []
    for chamado in chamados:
        bloco = nome_bloco(chamado)
        if bloco not in blocos:
            blocos.append(bloco)
    return sorted(blocos)


def filtrar_por_bloco(chamados, bloco):
    filtrados = []
    for chamado in chamados:
        if nome_bloco(chamado) == bloco:
            filtrados.append(chamado)
    return filtrados


# ---------------------------------------------------------------------------
# Cálculos (sem print)
# ---------------------------------------------------------------------------

def contar_por(chamados, campo, valores):
    """Dicionário {valor: quantidade}, mantendo a ordem padronizada de valores."""
    contagem = {}
    for valor in valores:
        contagem[valor] = 0
    for chamado in chamados:
        if chamado[campo] in contagem:
            contagem[chamado[campo]] += 1
    return contagem


def matriz_categoria_status(chamados):
    """Lista de listas: linha = categoria, coluna = status (ordem das constantes)."""
    matriz = []
    for _ in CATEGORIAS:
        matriz.append([0] * len(STATUS))
    for chamado in chamados:
        categoria = chamado["categoria"]
        status = chamado["status"]
        if categoria in CATEGORIAS and status in STATUS:
            matriz[CATEGORIAS.index(categoria)][STATUS.index(status)] += 1
    return matriz


def matriz_bloco_status(chamados, blocos):
    """Lista de listas: linha = bloco (torre), coluna = status."""
    matriz = []
    for _ in blocos:
        matriz.append([0] * len(STATUS))
    for chamado in chamados:
        bloco = nome_bloco(chamado)
        if bloco in blocos and chamado["status"] in STATUS:
            matriz[blocos.index(bloco)][STATUS.index(chamado["status"])] += 1
    return matriz


def montar_hierarquia(chamados):
    """Hierarquia bloco (torre) -> categoria -> lista de chamados.

    Só entram as categorias que têm chamados naquele bloco, para o painel não
    exibir grupos vazios.
    """
    hierarquia = {}
    for bloco in blocos_disponiveis(chamados):
        hierarquia[bloco] = {}
    for chamado in chamados:
        bloco = nome_bloco(chamado)
        categoria = chamado["categoria"]
        if categoria not in hierarquia[bloco]:
            hierarquia[bloco][categoria] = []
        hierarquia[bloco][categoria].append(chamado)
    return hierarquia


def calcular_indicadores(chamados, historico, referencia=None):
    """Indicadores do painel. referencia é o dia simulado usado como "hoje"."""
    if referencia is None:
        referencia = dia_referencia(chamados, historico)
    total = len(chamados)
    resolvidos = 0
    soma_resolucao = 0
    resolvidos_no_prazo = 0
    pendentes = 0
    soma_espera = 0
    atrasados = []
    urgentes_pendentes = 0
    criticos_atrasados = 0

    for chamado in chamados:
        abertura = converter_dia(chamado.get("dia_abertura"))
        fechamento = converter_dia(chamado.get("dia_fechamento"))
        prazo = prazo_de(chamado)
        if abertura is None:
            abertura = referencia  # sem dia válido: não conta tempo de espera
        if eh_pendente(chamado):
            pendentes += 1
            espera = referencia - abertura
            soma_espera += espera
            atrasado = prazo is not None and espera > prazo
            if atrasado:
                atrasados.append(chamado)
            # Atraso crítico: passou do prazo E a prioridade é urgente OU alta.
            if atrasado and (chamado["prioridade"] == "urgente"
                             or chamado["prioridade"] == "alta"):
                criticos_atrasados += 1
            if chamado["prioridade"] == "urgente":
                urgentes_pendentes += 1
        else:
            resolvidos += 1
            if fechamento is None:
                fechamento = abertura
            duracao = fechamento - abertura
            soma_resolucao += duracao
            if prazo is None or duracao <= prazo:
                resolvidos_no_prazo += 1

    tempo_medio = soma_resolucao / resolvidos if resolvidos > 0 else None
    espera_media = soma_espera / pendentes if pendentes > 0 else None
    return {
        "referencia": referencia,
        "total": total,
        "resolvidos": resolvidos,
        "pendentes": pendentes,
        "taxa_resolucao": percentual(resolvidos, total),
        "tempo_medio_resolucao": tempo_medio,
        "soma_resolucao": soma_resolucao,
        "resolvidos_no_prazo": resolvidos_no_prazo,
        "espera_media_pendentes": espera_media,
        "soma_espera": soma_espera,
        "atrasados": atrasados,
        "urgentes_pendentes": urgentes_pendentes,
        "criticos_atrasados": criticos_atrasados,
        "eventos": len(historico),
    }


def ultimos_eventos(historico, quantidade=5):
    """Usa o histórico como pilha: o topo (último item) é o evento mais recente."""
    pilha = list(historico)  # cópia, para não esvaziar o histórico original
    recentes = []
    while pilha and len(recentes) < quantidade:
        recentes.append(pilha.pop())
    return recentes


def mais_frequentes(contagem):
    """Chaves com a maior contagem (pode haver empate). Vazio se tudo for zero."""
    maior = 0
    for valor in contagem.values():
        if valor > maior:
            maior = valor
    if maior == 0:
        return [], 0
    chaves = []
    for chave, valor in contagem.items():
        if valor == maior:
            chaves.append(chave)
    return chaves, maior


def pendentes_por_bloco(chamados):
    contagem = {}
    for bloco in blocos_disponiveis(chamados):
        contagem[bloco] = 0
    for chamado in chamados:
        if eh_pendente(chamado):
            contagem[nome_bloco(chamado)] += 1
    return contagem


def gerar_conclusao(chamados, indicadores):
    """Interpretação curta dos números, escrita a partir de regras simples."""
    if not chamados:
        return ["Não há chamados válidos para interpretar."]
    frases = []
    categorias, qtd = mais_frequentes(contar_por(chamados, "categoria", CATEGORIAS))
    nomes = [ROTULOS_CATEGORIA[c] for c in categorias]
    if len(nomes) == 1:
        frases.append(f"A categoria com mais chamados é {nomes[0]} ({qtd}).")
    else:
        frases.append(f"Há empate entre {', '.join(nomes)} ({qtd} chamados cada).")

    blocos, qtd = mais_frequentes(pendentes_por_bloco(chamados))
    if qtd == 0:
        frases.append("Nenhum bloco tem chamados pendentes.")
    elif len(blocos) == 1:
        frases.append(f"O bloco/torre com mais pendências é {blocos[0]} ({qtd}).")
    else:
        frases.append(f"Os blocos/torres {', '.join(blocos)} empatam em pendências ({qtd} cada).")

    taxa = indicadores["taxa_resolucao"]
    if taxa < 50:
        frases.append(f"Só {taxa:.1f}% dos chamados foram resolvidos: a maior parte segue em aberto.")
    else:
        frases.append(f"{taxa:.1f}% dos chamados já foram resolvidos.")

    atrasados = len(indicadores["atrasados"])
    if atrasados > 0 and indicadores["urgentes_pendentes"] > 0:
        frases.append(f"{atrasados} pendência(s) passaram do prazo, e há "
                      f"{indicadores['urgentes_pendentes']} urgente(s) sem solução: "
                      "vale priorizar esses casos.")
    elif atrasados > 0:
        frases.append(f"{atrasados} pendência(s) passaram do prazo previsto.")
    else:
        frases.append("Todas as pendências estão dentro do prazo previsto.")
    frases.append("Os dados são simulados; servem para treinar a análise, não "
                  "para avaliar um condomínio real.")
    return frases


# ---------------------------------------------------------------------------
# Exibição
# ---------------------------------------------------------------------------

def titulo(texto):
    print("\n" + LINHA)
    print(texto.upper())
    print(LINHA)


def tabela_contagem(rotulo, contagem, rotulos, total):
    """Tabela com quantidade, proporção e barra para cada valor."""
    maximo = max(contagem.values(), default=0)
    print(f"{rotulo:<22}{'Qtd':>5}{'%':>8}  Gráfico")
    print(SEPARADOR)
    for chave, valor in contagem.items():
        print(f"{rotulos.get(chave, chave):<22}{valor:>5}{percentual(valor, total):>7.1f}%  "
              f"{barra(valor, maximo)}")
    print(SEPARADOR)
    print(f"{'Total':<22}{total:>5}{percentual(total, total):>7.1f}%")


def exibir_matriz(rotulo, linhas, matriz):
    print(f"{rotulo:<18}" + "".join(f"{c:>11}" for c in COLUNAS_STATUS) + f"{'Total':>8}")
    print(SEPARADOR)
    totais_colunas = [0] * len(STATUS)
    for i in range(len(linhas)):
        soma = 0
        texto = f"{linhas[i]:<18}"
        for j in range(len(STATUS)):
            texto += f"{matriz[i][j]:>11}"
            soma += matriz[i][j]
            totais_colunas[j] += matriz[i][j]
        print(texto + f"{soma:>8}")
    print(SEPARADOR)
    print(f"{'Total':<18}" + "".join(f"{t:>11}" for t in totais_colunas)
          + f"{sum(totais_colunas):>8}")
    print("Legenda: Em atend. = em atendimento; Ag. terc. = aguardando terceiro; "
          "Resolv. = resolvido.")


def exibir_hierarquia(chamados):
    hierarquia = montar_hierarquia(chamados)
    for bloco, categorias in hierarquia.items():
        total_bloco = 0
        for lista in categorias.values():
            total_bloco += len(lista)
        print(f"\n{bloco} ({total_bloco} chamado(s))")
        for categoria in CATEGORIAS:
            if categoria in categorias:
                lista = categorias[categoria]
                print(f"  └ {ROTULOS_CATEGORIA[categoria]} ({len(lista)})")
                for chamado in lista:
                    prioridade = chamado["prioridade"]
                    if prioridade == "urgente":
                        prioridade = "URGENTE"
                    print(f"      {chamado['protocolo']} | {chamado['area']} | "
                          f"{rotulo_status(chamado['status'])} | {prioridade}")


def exibir_indicadores(indicadores):
    ind = indicadores
    print(f"Dia simulado de referência: {ind['referencia']} (maior dia registrado na base)")
    print(SEPARADOR)
    print(f"Taxa de resolução: {ind['resolvidos']} resolvidos / {ind['total']} chamados x 100 "
          f"= {ind['taxa_resolucao']:.1f}%")
    if ind["tempo_medio_resolucao"] is None:
        print("Tempo médio de resolução: sem chamados resolvidos ainda.")
    else:
        print(f"Tempo médio de resolução: soma(fechamento - abertura) / resolvidos = "
              f"{ind['soma_resolucao']} / {ind['resolvidos']} = "
              f"{ind['tempo_medio_resolucao']:.1f} dia(s)")
        print(f"Resolvidos dentro do prazo da prioridade: {ind['resolvidos_no_prazo']} "
              f"de {ind['resolvidos']}")
    if ind["espera_media_pendentes"] is None:
        print("Espera média das pendências: não há pendências.")
    else:
        print(f"Espera média das pendências: soma(referência - abertura) / pendentes = "
              f"{ind['soma_espera']} / {ind['pendentes']} = "
              f"{ind['espera_media_pendentes']:.1f} dia(s)")
    prazos = ", ".join(f"{p} {d} dia(s)" for p, d in PRAZOS.items())
    print(f"Pendências fora do prazo ({prazos}): {len(ind['atrasados'])} de {ind['pendentes']}")
    print(f"  das quais com prioridade urgente ou alta: {ind['criticos_atrasados']}")
    for chamado in ind["atrasados"]:
        espera = ind["referencia"] - converter_dia(chamado["dia_abertura"])
        print(f"   {chamado['protocolo']} | {nome_bloco(chamado)} | {chamado['prioridade']} | "
              f"aberto há {espera} dia(s), prazo {prazo_de(chamado)}")


def exibir_ultimos_eventos(historico, quantidade=5):
    recentes = ultimos_eventos(historico, quantidade)
    if not recentes:
        print("Nenhuma atualização registrada.")
        return
    for evento in recentes:
        dia, anterior, novo = dados_evento(evento)
        print(f"Dia {dia if dia is not None else '?':>3} | {evento.get('protocolo', '?')} | "
              f"{rotulo_status(anterior)} -> {rotulo_status(novo)} | "
              f"{evento.get('observacao', '')}")


def exibir_dashboard(chamados, historico):
    """Painel completo do condomínio, com todos os blocos (torres)."""
    titulo("Dashboard de chamados do condomínio")
    if not chamados:
        print("Nenhum chamado válido cadastrado. Cadastre um chamado para ver o painel.")
        return
    indicadores = calcular_indicadores(chamados, historico)
    blocos = blocos_disponiveis(chamados)
    print(f"Chamados válidos: {indicadores['total']} | Pendentes: {indicadores['pendentes']} | "
          f"Resolvidos: {indicadores['resolvidos']} | Blocos/torres: {len(blocos)} | "
          f"Eventos: {indicadores['eventos']}")
    print("Fonte: data/chamados.csv e data/historico.csv (registros inválidos não entram).")

    titulo("1. Chamados por status")
    tabela_contagem("Status", contar_por(chamados, "status", STATUS), ROTULOS_STATUS,
                    indicadores["total"])

    titulo("2. Chamados por categoria")
    tabela_contagem("Categoria", contar_por(chamados, "categoria", CATEGORIAS),
                    ROTULOS_CATEGORIA, indicadores["total"])

    titulo("3. Matriz categoria x status")
    nomes = [ROTULOS_CATEGORIA[c] for c in CATEGORIAS]
    exibir_matriz("Categoria", nomes, matriz_categoria_status(chamados))

    titulo("4. Matriz bloco/torre x status")
    exibir_matriz("Bloco/torre", blocos, matriz_bloco_status(chamados, blocos))

    titulo("5. Hierarquia bloco/torre -> categoria -> chamados")
    exibir_hierarquia(chamados)

    titulo("6. Indicadores")
    exibir_indicadores(indicadores)

    titulo("7. Últimas atualizações (topo da pilha)")
    exibir_ultimos_eventos(historico)

    titulo("8. Conclusão")
    for frase in gerar_conclusao(chamados, indicadores):
        print(f"- {frase}")


def exibir_painel_bloco(chamados, historico, bloco):
    """Painel de um único bloco (torre)."""
    do_bloco = filtrar_por_bloco(chamados, bloco)
    titulo(f"Painel do {bloco}")
    if not do_bloco:
        print(f"Nenhum chamado encontrado para {bloco}.")
        return
    protocolos = []
    for chamado in do_bloco:
        protocolos.append(chamado["protocolo"])
    eventos_bloco = []
    for evento in historico:
        if evento["protocolo"] in protocolos:
            eventos_bloco.append(evento)
    # A referência continua sendo o dia da base inteira, para comparar blocos.
    indicadores = calcular_indicadores(do_bloco, eventos_bloco,
                                       dia_referencia(chamados, historico))
    print(f"Chamados: {indicadores['total']} | Pendentes: {indicadores['pendentes']} | "
          f"Resolvidos: {indicadores['resolvidos']}")
    print()
    tabela_contagem("Status", contar_por(do_bloco, "status", STATUS), ROTULOS_STATUS,
                    indicadores["total"])
    print()
    tabela_contagem("Categoria", contar_por(do_bloco, "categoria", CATEGORIAS),
                    ROTULOS_CATEGORIA, indicadores["total"])
    print("\nChamados do bloco:")
    exibir_hierarquia(do_bloco)
    print()
    exibir_indicadores(indicadores)
    print("\nÚltimas atualizações do bloco:")
    exibir_ultimos_eventos(eventos_bloco)


if __name__ == "__main__":
    from dados import carregar, carregar_historico

    try:
        base, _ = carregar()
        exibir_dashboard(base, carregar_historico(base))
    except (ValueError, OSError) as erro:
        print(f"Erro ao carregar os dados: {erro}")
