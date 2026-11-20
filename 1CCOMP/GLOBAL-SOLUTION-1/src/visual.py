import os
import sys

CORES = {
    "marte": "38;5;208",
    "titulo": "1;38;5;208",
    "ok": "32",
    "erro": "31",
    "destaque": "1",
    "suave": "2",
}
CORES_STATUS = {
    "aberto": "31",
    "em_atendimento": "33",
    "aguardando_terceiro": "35",
    "resolvido": "32",
}

if os.name == "nt":
    os.system("")

BANNER = r"""
        *          .            +             .          *
    .           _.-~~~~~~~~~~~~~~~~~-._            .
         +   .-'      C O L Ô N I A      '-.    *
           /           A U R O R A          \
      .   /    [_]      [_]      [_]     [_]  \        +
  ~~~~~~~/______________________________________\~~~~~~~~~
      ·  HABITAT MARTE-1  ·  CÚPULA PRESSURIZADA  ·
"""


def usar_cores():
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def cor(texto, nome):
    codigo = CORES.get(nome) or CORES_STATUS.get(nome)
    if not codigo or not usar_cores():
        return texto
    return f"\033[{codigo}m{texto}\033[0m"


def mostrar_banner(chamados, historico, fila):
    print(cor(BANNER, "marte"))
    print(cor("  NEXCONDO · CENTRAL DE CHAMADOS DO CONDOMÍNIO", "titulo"))
    print(cor("  Manutenção das áreas comuns dos módulos habitacionais · uma solução NexoTech", "suave"))
    print(f"  {len(chamados)} chamados válidos · "
          f"{len(historico)} eventos registrados · {len(fila)} aguardando triagem")


def interativo():
    return sys.stdin.isatty() and sys.stdout.isatty()


def limpar_tela():
    if interativo():
        print("\033[2J\033[3J\033[H", end="", flush=True)


def pausar():
    if interativo():
        input(cor("\nPressione Enter para voltar ao menu…", "suave"))


def mostrar_cabecalho(chamados, historico, fila):
    pendentes = sum(1 for chamado in chamados if chamado["status"] != "resolvido")
    print(cor("  NEXCONDO", "titulo") + cor(" · Colônia Aurora · Habitat Marte-1", "suave"))
    print(f"  {len(chamados)} chamados · {pendentes} pendentes · {len(fila)} na fila · {len(historico)} eventos")


def mostrar_menu():
    linha = cor("  " + "─" * 58, "marte")
    print(linha)
    print(cor("   NEXCONDO · PAINEL DE CONTROLE DA COLÔNIA AURORA", "titulo"))
    print(linha)
    opcoes = [
        ("1", "Listar chamados", "6", "Atualizar status"),
        ("2", "Abrir chamado", "7", "Últimas atualizações"),
        ("3", "Consultar protocolo", "8", "Painel de indicadores"),
        ("4", "Filtrar", "9", "Visão por bloco"),
        ("5", "Atender próximo da fila", "0", "Sair da estação"),
    ]
    for n1, texto1, n2, texto2 in opcoes:
        print(f"   {cor(n1, 'destaque')} - {texto1:<25}{cor(n2, 'destaque')} - {texto2}")
    print(f"  {cor('10', 'destaque')} - Abrir dashboard web no navegador (com os dados desta sessão)")
    print(linha)


def status(texto):
    return cor(texto, texto)


def ok(mensagem):
    print(cor(f"[OK] {mensagem}", "ok"))


def erro(mensagem):
    print(cor(f"[!] {mensagem}", "erro"))
