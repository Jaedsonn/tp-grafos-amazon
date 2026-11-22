import heapq
from dataclasses import dataclass

import numpy as np

from src.comum.tipos import AdjacenciaPonderada


@dataclass(frozen=True)
class MatrizDistancias:
    """Saída do Floyd-Warshall: distâncias[i][j] entre vertices[i] e vertices[j]"""

    vertices: list[str]
    distancias: np.ndarray


def calcular_dijkstra(adjacencia: AdjacenciaPonderada, origem: str) -> dict[str, float]:
    """
    :param adjacencia: grafo com distâncias não negativas
    :param origem: vértice inicial, presente em adjacencia
    :return: menor distância da origem até cada vértice alcançável

    Exemplo:
        >>> calcular_dijkstra({"a": {"b": 1.0, "c": 4.0}, "b": {"a": 1.0, "c": 1.0}, "c": {"a": 4.0, "b": 1.0}}, "a")
        {'a': 0.0, 'b': 1.0, 'c': 2.0}
    """
    if origem not in adjacencia:
        raise KeyError(
            f"origem {origem!r} não está no grafo; esperado um vértice existente"
        )
    distancias: dict[str, float] = {}
    fila = [(0.0, origem)]
    while fila:
        distancia, atual = heapq.heappop(fila)
        if atual in distancias:
            continue
        distancias[atual] = distancia
        for vizinho, peso in adjacencia[atual].items():
            if vizinho not in distancias:
                heapq.heappush(fila, (distancia + peso, vizinho))
    return distancias


def calcular_bellman_ford(
    adjacencia: AdjacenciaPonderada, origem: str
) -> dict[str, float]:
    """
    :param adjacencia: grafo ponderado; num não dirigido cada aresta relaxa nos dois sentidos
    :param origem: vértice inicial, presente em adjacencia
    :return: menor distância da origem até cada vértice alcançável

    Exemplo:
        >>> calcular_bellman_ford({"a": {"b": 1.0, "c": 4.0}, "b": {"a": 1.0, "c": 1.0}, "c": {"a": 4.0, "b": 1.0}}, "a")
        {'a': 0.0, 'b': 1.0, 'c': 2.0}
    """
    if origem not in adjacencia:
        raise KeyError(
            f"origem {origem!r} não está no grafo; esperado um vértice existente"
        )
    distancias = {origem: 0.0}
    for _ in range(len(adjacencia) - 1):
        # parada antecipada: se uma rodada não relaxa nada, as distâncias já são finais
        if not relaxar_todas_as_arestas(adjacencia, distancias):
            return distancias
    if relaxar_todas_as_arestas(adjacencia, distancias):
        raise ValueError(
            "ciclo negativo alcançável; esperado grafo sem ciclos negativos"
        )
    return distancias


def relaxar_todas_as_arestas(
    adjacencia: AdjacenciaPonderada, distancias: dict[str, float]
) -> bool:
    """
    :param adjacencia: grafo ponderado
    :param distancias: estimativas atuais, atualizadas no lugar
    :return: True se alguma distância diminuiu nesta rodada

    Exemplo:
        >>> d = {"a": 0.0}; relaxar_todas_as_arestas({"a": {"b": 2.0}, "b": {"a": 2.0}}, d), d
        (True, {'a': 0.0, 'b': 2.0})
    """
    mudou = False
    for u, vizinhos in adjacencia.items():
        if u not in distancias:
            continue
        for v, peso in vizinhos.items():
            if distancias[u] + peso < distancias.get(v, float("inf")):
                distancias[v] = distancias[u] + peso
                mudou = True
    return mudou


def calcular_floyd_warshall(adjacencia: AdjacenciaPonderada) -> MatrizDistancias:
    """
    :param adjacencia: grafo ponderado (use subgrafos: memória O(n²) e tempo O(n³))
    :return: MatrizDistancias com todos os pares

    Exemplo:
        >>> r = calcular_floyd_warshall({"a": {"b": 1.0}, "b": {"a": 1.0, "c": 1.0}, "c": {"b": 1.0}})
        >>> r.vertices, float(r.distancias[0][2])
        (['a', 'b', 'c'], 2.0)
    """
    vertices = sorted(adjacencia)
    indice = {v: i for i, v in enumerate(vertices)}
    distancias = np.full((len(vertices), len(vertices)), np.inf)
    np.fill_diagonal(distancias, 0.0)
    for u, vizinhos in adjacencia.items():
        for v, peso in vizinhos.items():
            distancias[indice[u], indice[v]] = peso
    for k in range(len(vertices)):
        np.minimum(
            distancias, distancias[:, k, None] + distancias[None, k, :], out=distancias
        )
    return MatrizDistancias(vertices, distancias)
