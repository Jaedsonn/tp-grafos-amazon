from dataclasses import dataclass

import igraph
import networkx as nx

from src.comum.tipos import Adjacencia, AdjacenciaPonderada, ArestaJogos


@dataclass(frozen=True)
class MedidasExatas:
    """Medidas de distância exatas, inviáveis em Python puro (n(n+m) ≈ 7·10⁹ passos)"""

    diametro: int
    raio: int
    caminho_medio: float


@dataclass(frozen=True)
class ConferenciaClusterizacao:
    """Referência de biblioteca para conferir o código próprio"""

    clusterizacao_media: float
    triangulos: int


def converter_para_igraph(adjacencia: Adjacencia) -> igraph.Graph:
    """
    :param adjacencia: grafo não dirigido com rótulos str
    :return: igraph.Graph não dirigido e sem pesos, com o rótulo no atributo "name"

    Exemplo:
        >>> converter_para_igraph({"a": {"b"}, "b": {"a"}}).ecount()
        1
    """
    vertices = sorted(adjacencia)
    indice = {v: i for i, v in enumerate(vertices)}
    arestas = [(indice[p], indice[q]) for p in vertices for q in adjacencia[p] if p < q]
    grafo = igraph.Graph(n=len(vertices), edges=arestas, directed=False)
    grafo.vs["name"] = vertices
    return grafo


def medir_distancias_exatas(adjacencia: Adjacencia) -> MedidasExatas:
    """
    :param adjacencia: grafo não dirigido e conexo
    :return: diâmetro, raio e caminho médio L, em saltos

    Exemplo:
        >>> medir_distancias_exatas({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}})
        MedidasExatas(diametro=2, raio=1, caminho_medio=1.3333333333333333)
    """
    grafo = converter_para_igraph(adjacencia)
    return MedidasExatas(
        diametro=int(grafo.diameter(directed=False)),
        raio=int(grafo.radius()),
        caminho_medio=float(grafo.average_path_length(directed=False)),
    )


def conferir_clusterizacao(adjacencia: Adjacencia) -> ConferenciaClusterizacao:
    """
    :param adjacencia: grafo não dirigido
    :return: C médio (C_v = 0 quando k_v < 2) e nº de triângulos segundo o igraph

    Exemplo:
        >>> conferir_clusterizacao({"1": {"2", "3"}, "2": {"1", "3"}, "3": {"1", "2"}})
        ConferenciaClusterizacao(clusterizacao_media=1.0, triangulos=1)
    """
    grafo = converter_para_igraph(adjacencia)
    # mode="zero" usa a mesma convenção do código próprio para vértices de grau < 2
    media = grafo.transitivity_avglocal_undirected(mode="zero")
    return ConferenciaClusterizacao(float(media), len(grafo.list_triangles()))


@dataclass(frozen=True)
class ReferenciaAlgoritmos:
    """Resultados do networkx usados para conferir os algoritmos próprios da Parte II"""

    distancias_dijkstra: dict[str, float]
    custo_arvore_geradora: float
    pontes: set[ArestaJogos]
    articulacoes: set[str]
    euleriano: bool


def converter_para_networkx(adjacencia: AdjacenciaPonderada) -> nx.Graph:
    """
    :param adjacencia: grafo com distâncias d = 1/w
    :return: nx.Graph com o atributo de aresta "d"

    Exemplo:
        >>> converter_para_networkx({"a": {"b": 0.5}, "b": {"a": 0.5}}).edges["a", "b"]["d"]
        0.5
    """
    grafo = nx.Graph()
    grafo.add_nodes_from(adjacencia)
    grafo.add_weighted_edges_from(
        ((u, v, d) for u, vizinhos in adjacencia.items() for v, d in vizinhos.items()),
        weight="d",
    )
    return grafo


def calcular_referencia(
    adjacencia: AdjacenciaPonderada, origem: str
) -> ReferenciaAlgoritmos:
    """
    :param adjacencia: grafo com distâncias d = 1/w, conexo
    :param origem: origem do Dijkstra de referência
    :return: ReferenciaAlgoritmos segundo o networkx

    Exemplo:
        >>> r = calcular_referencia({"a": {"b": 1.0}, "b": {"a": 1.0}}, "a")
        >>> r.custo_arvore_geradora, r.pontes, r.euleriano
        (1.0, {('a', 'b')}, False)
    """
    grafo = converter_para_networkx(adjacencia)
    arvore = nx.minimum_spanning_tree(grafo, weight="d")
    return ReferenciaAlgoritmos(
        distancias_dijkstra=dict(
            nx.single_source_dijkstra_path_length(grafo, origem, weight="d")
        ),
        custo_arvore_geradora=float(arvore.size(weight="d")),
        pontes={(min(u, v), max(u, v)) for u, v in nx.bridges(grafo)},
        articulacoes=set(nx.articulation_points(grafo)),
        euleriano=nx.is_eulerian(grafo),
    )
