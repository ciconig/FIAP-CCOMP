import json
import webbrowser
from pathlib import Path

from dados import ARQUIVO, CAMPOS, _ler_csv
from visual import erro, ok

PASTA_WEB = Path(__file__).resolve().parent.parent / "web"


def exportar(chamados, historico, caminho_csv=ARQUIVO, destino=None):
    atuais = {chamado["protocolo"]: chamado for chamado in chamados}
    linhas = []
    for _, linha in _ler_csv(caminho_csv, CAMPOS):
        linhas.append(atuais.pop(linha["protocolo"], linha))
    linhas.extend(atuais.values())
    destino = Path(destino) if destino else PASTA_WEB / "dados.js"
    destino.write_text(
        f"window.DADOS_CHAMADOS = {json.dumps(linhas, ensure_ascii=False, indent=1)};\n"
        f"window.DADOS_HISTORICO = {json.dumps(historico, ensure_ascii=False, indent=1)};\n",
        encoding="utf-8",
    )
    return len(linhas), len(historico)


def abrir_painel_web(chamados, historico):
    pagina = PASTA_WEB / "index.html"
    if not pagina.exists():
        erro(f"Painel web não encontrado em {pagina}.")
        return None
    total, eventos = exportar(chamados, historico)
    link = pagina.as_uri()
    ok(f"Painel atualizado com {total} chamados e {eventos} eventos desta sessão.")
    print(f"Link do dashboard: {link}")
    if not webbrowser.open(link):
        print("Não foi possível abrir o navegador automaticamente; copie o link acima.")
    return link
