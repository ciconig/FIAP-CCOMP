import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / "src"))

from dados import ARQUIVO, CAMPOS, _ler_csv, carregar, carregar_historico  # noqa: E402

linhas = [linha for _, linha in _ler_csv(ARQUIVO, CAMPOS)]
chamados, _ = carregar(exibir_avisos=False)
historico = carregar_historico(chamados)

conteudo = (
    f"window.DADOS_CHAMADOS = {json.dumps(linhas, ensure_ascii=False, indent=1)};\n"
    f"window.DADOS_HISTORICO = {json.dumps(historico, ensure_ascii=False, indent=1)};\n"
)
(PASTA / "dados.js").write_text(conteudo, encoding="utf-8")
print(f"web/dados.js: {len(linhas)} chamados e {len(historico)} eventos.")
