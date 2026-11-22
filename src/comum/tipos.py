from dataclasses import dataclass

ParAvaliacao = tuple[str, str]
ArestaJogos = tuple[str, str]
Adjacencia = dict[str, set[str]]
PesosArestas = dict[ArestaJogos, int]
AdjacenciaPonderada = dict[str, dict[str, float]]


@dataclass(frozen=True)
class Jogo:
    """Um jogo do grafo"""

    asin: str
    titulo: str
    plataforma: str
    tipo: str


@dataclass(frozen=True)
class EtapaFunil:
    """Registro de resumo do grafo após cada etapa do pré-processamento (funil)"""

    nome: str
    usuarios: int | None
    jogos: int
    arestas: int
