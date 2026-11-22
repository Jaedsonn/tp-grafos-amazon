from pathlib import Path

SEED: int = 42

CAP_USUARIO: int = 50
MIN_AVALIACOES_JOGO: int = 5
MIN_PESO: int = 2

RAIZ: Path = Path(__file__).resolve().parent.parent
ARQ_AVALIACOES: Path = RAIZ / "data" / "raw" / "Video_Games.csv"
ARQ_METADADOS: Path = RAIZ / "data" / "raw" / "meta_Video_Games.json.gz"
DIR_PROCESSADO: Path = RAIZ / "data" / "processado"
