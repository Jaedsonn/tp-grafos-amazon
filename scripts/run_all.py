"""
Executa o trabalho inteiro, na ordem, sem abrir o Jupyter.

    uv run python scripts/run_all.py                 # ETL (se houver dados brutos) e notebooks
    uv run python scripts/run_all.py --sem-parte2    # pula a Parte II, que mede tempos
    uv run python scripts/run_all.py --notebooks 04 05

Sem os arquivos de data/raw/, o ETL é pulado e os notebooks usam os dados tratados de
data/processado/. Na Parte III, o nulo bipartido e a sensibilidade ao limiar são lidos de
results/, gravados pela última execução com os dados brutos.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.comum import config  # noqa: E402

NOTEBOOKS = {
    "01": "01_parte1.ipynb",
    "02": "02_parte2.ipynb",
    "03": "03_parte3.ipynb",
    "04": "04_consoles.ipynb",
    "05": "05_modelos.ipynb",
}


def executar_notebook(nome: str) -> None:
    """
    :param nome: arquivo em notebooks/, executado no lugar, com as saídas gravadas

    Exemplo:
        executar_notebook("04_consoles.ipynb")
    """
    caminho = RAIZ / "notebooks" / nome
    notebook = nbformat.read(caminho, as_version=4)
    NotebookClient(
        notebook,
        timeout=3600,
        kernel_name="python3",
        resources={"metadata": {"path": str(caminho.parent)}},
    ).execute()
    nbformat.write(notebook, caminho)


def etapa(titulo: str, acao) -> None:
    inicio = time.perf_counter()
    print(f"→ {titulo}", flush=True)
    acao()
    print(f"  ok ({time.perf_counter() - inicio:.0f} s)", flush=True)


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    argumentos.add_argument(
        "--notebooks", nargs="*", choices=NOTEBOOKS, default=list(NOTEBOOKS)
    )
    argumentos.add_argument(
        "--sem-parte2", action="store_true", help="não remede os tempos"
    )
    opcoes = argumentos.parse_args()

    if config.ARQ_AVALIACOES.exists() and config.ARQ_METADADOS.exists():
        etapa(
            "pré-processamento (src.etl.pipeline)",
            lambda: subprocess.run(
                [sys.executable, "-m", "src.etl.pipeline"], cwd=RAIZ, check=True
            ),
        )
    else:
        print(
            "→ pré-processamento pulado: data/raw/ sem os arquivos brutos; usando data/processado/"
        )
    for chave in opcoes.notebooks:
        if chave == "02" and opcoes.sem_parte2:
            print("→ Parte II pulada (--sem-parte2)")
            continue
        etapa(
            f"notebook {NOTEBOOKS[chave]}",
            lambda nome=NOTEBOOKS[chave]: executar_notebook(nome),
        )
    print("Pronto: tabelas em results/ e figuras em imagens/.")


if __name__ == "__main__":
    main()
