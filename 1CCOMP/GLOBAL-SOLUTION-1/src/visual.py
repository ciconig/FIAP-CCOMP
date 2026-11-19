"""Identidade visual do terminal: Colônia Aurora, condomínio em Marte.

As cores são só um reforço: toda informação também aparece em texto. Elas
ficam desligadas quando a saída não é um terminal (testes, arquivos) ou
quando a variável de ambiente NO_COLOR está definida.
"""

import os
import sys

# Códigos ANSI: 31 vermelho, 32 verde, 33 amarelo, 35 magenta, 36 ciano, 1 negrito, 2 fraco.
CORES = {
    "marte": "38;5;208",  # laranja marciano
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
    os.system("")  # ativa as sequências ANSI no console do Windows

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
    print(cor("  CENTRAL DE CHAMADOS DO CONDOMÍNIO", "titulo"))
    print(cor("  Manutenção das áreas comuns dos módulos habitacionais", "suave"))
    print(f"  {len(chamados)} chamados válidos · "
          f"{len(historico)} eventos registrados · {len(fila)} aguardando triagem")


def mostrar_menu():
    linha = cor("  " + "─" * 58, "marte")
    print("\n" + linha)
    print(cor("   PAINEL DE CONTROLE · COLÔNIA AURORA", "titulo"))
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
    print(linha)


def status(texto):
    return cor(texto, texto)


def ok(mensagem):
    print(cor(f"[OK] {mensagem}", "ok"))


def erro(mensagem):
    print(cor(f"[!] {mensagem}", "erro"))
