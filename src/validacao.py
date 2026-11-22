from dataclasses import dataclass

import igraph

from src.tipos import Adjacencia


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
