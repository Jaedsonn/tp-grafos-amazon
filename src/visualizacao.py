from collections import Counter
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.figure import Figure

from src.tipos import Jogo, PesosArestas

MAX_PLATAFORMAS_NA_LEGENDA: int = 8
COR_OUTRAS: str = "#B4B2A9"


def salvar_figura(figura: Figure, destino: Path) -> None:
    """
    :param figura: figura do matplotlib
    :param destino: caminho sem extensão; grava .pdf (relatório) e .png (README e notebook)

    Exemplo:
        salvar_figura(figura, config.RAIZ / "imagens" / "parte1_graus")
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    for extensao in ("pdf", "png"):
        figura.savefig(
            destino.with_suffix(f".{extensao}"), dpi=200, bbox_inches="tight"
        )


def plotar_distribuicao_graus(
    distribuicao: dict[int, int], ccdf: dict[int, float]
) -> Figure:
    """
    :param distribuicao: histograma k -> quantidade
    :param ccdf: P(K >= k) por k
    :return: figura com P(k) e CCDF lado a lado, ambos em log-log

    Exemplo:
        figura = plotar_distribuicao_graus({1: 3, 2: 1}, {1: 1.0, 2: 0.25})
    """
    total = sum(distribuicao.values())
    figura, (eixo_pk, eixo_ccdf) = plt.subplots(1, 2, figsize=(10, 4))
    eixo_pk.loglog(
        list(distribuicao), [q / total for q in distribuicao.values()], "o", ms=3
    )
    eixo_pk.set(xlabel="grau k", ylabel="P(k)", title="Distribuição de graus")
    eixo_ccdf.loglog(list(ccdf), list(ccdf.values()), "-", lw=1.5)
    eixo_ccdf.set(xlabel="grau k", ylabel="P(K ≥ k)", title="CCDF")
    for eixo in (eixo_pk, eixo_ccdf):
        eixo.grid(True, which="major", alpha=0.3)
    figura.tight_layout()
    return figura


def colorir_por_plataforma(
    vertices: list[str], jogos: dict[str, Jogo]
) -> tuple[list[str], dict[str, str]]:
    """
    :param vertices: vértices na ordem do desenho
    :param jogos: catálogo com a plataforma de cada vértice
    :return: cor de cada vértice e legenda plataforma -> cor (as demais ficam cinza)

    Exemplo:
        >>> cores, legenda = colorir_por_plataforma(["a"], {"a": Jogo("a", "t", "Wii", "Games")})
        >>> list(legenda)
        ['Wii']
    """
    frequencia = Counter(jogos[v].plataforma for v in vertices)
    principais = [p for p, _ in frequencia.most_common(MAX_PLATAFORMAS_NA_LEGENDA)]
    paleta = plt.get_cmap("tab10").colors
    legenda = {p: matplotlib.colors.to_hex(paleta[i]) for i, p in enumerate(principais)}
    return [legenda.get(jogos[v].plataforma, COR_OUTRAS) for v in vertices], legenda


def desenhar_subgrafo(
    pesos: PesosArestas, jogos: dict[str, Jogo], graus: dict[str, int], semente: int
) -> Figure:
    """
    :param pesos: arestas do subgrafo a desenhar
    :param jogos: catálogo para cor (plataforma) e rótulos (título)
    :param graus: grau de cada vértice no grafo completo, que define o tamanho do nó
    :param semente: SEED do layout por forças, para a figura ser reprodutível
    :return: figura com cor por plataforma, tamanho por grau e os 10 maiores hubs rotulados

    Exemplo:
        figura = desenhar_subgrafo(pesos_nucleo, grafo.jogos, graus, config.SEED)
    """
    grafo = nx.Graph()
    grafo.add_weighted_edges_from((p, q, w) for (p, q), w in pesos.items())
    vertices = list(grafo.nodes)
    posicoes = nx.spring_layout(grafo, weight="weight", seed=semente)
    cores, legenda = colorir_por_plataforma(vertices, jogos)
    figura, eixo = plt.subplots(figsize=(10, 10))
    nx.draw_networkx_edges(grafo, posicoes, ax=eixo, alpha=0.05, width=0.5)
    tamanhos = [graus[v] / 8 for v in vertices]
    nx.draw_networkx_nodes(
        grafo, posicoes, ax=eixo, node_color=cores, node_size=tamanhos
    )
    hubs = sorted(vertices, key=graus.__getitem__, reverse=True)[:10]
    rotulos = {v: jogos[v].titulo[:28] for v in hubs}
    nx.draw_networkx_labels(grafo, posicoes, labels=rotulos, ax=eixo, font_size=7)
    for plataforma, cor in legenda.items():
        eixo.scatter([], [], c=cor, label=plataforma)
    eixo.legend(loc="lower left", fontsize=8, frameon=False)
    eixo.set_axis_off()
    return figura
