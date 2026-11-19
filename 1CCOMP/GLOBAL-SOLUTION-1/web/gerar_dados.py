import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dados import carregar, carregar_historico  # noqa: E402
from painel_web import exportar  # noqa: E402

chamados, _ = carregar(exibir_avisos=False)
total, eventos = exportar(chamados, carregar_historico(chamados))
print(f"web/dados.js: {total} chamados e {eventos} eventos.")
