"""
Diâmetro, raio e caminho médio exatos, com uma BFS a partir de cada vértice.

Para que n BFS caibam em poucos minutos em Python, o grafo é convertido em listas de
inteiros (índices contíguos), e as origens são divididas entre processos.
"""

from dataclasses import dataclass
from multiprocessing import get_context

from src.comum.tipos import Adjacencia

_VIZINHOS: list[list[int]] = []


@dataclass(frozen=True)
class DistanciasExatas:
    """Medidas de distância em saltos de um grafo conexo, a partir de todas as origens"""

    diametro: int
    raio: int
    caminho_medio: float
    pares: int
    centro: list[str]


def indexar(adjacencia: Adjacencia) -> tuple[list[str], list[list[int]]]:
    """
    :param adjacencia: grafo não dirigido
    :return: (vértices em ordem estável, vizinhos de cada índice como lista de índices)

    Exemplo:
        >>> indexar({"b": {"a"}, "a": {"b"}})
        (['a', 'b'], [[1], [0]])
    """
    vertices = sorted(adjacencia)
    indice = {v: i for i, v in enumerate(vertices)}
    return vertices, [sorted(indice[w] for w in adjacencia[v]) for v in vertices]


def medir_origem(vizinhos: list[list[int]], origem: int) -> tuple[int, int, int]:
    """
    BFS sobre listas de inteiros.

    :param vizinhos: vizinhos de cada índice
    :param origem: índice de partida
    :return: (excentricidade, soma das distâncias, vértices alcançados, sem contar a origem)

    Exemplo:
        >>> medir_origem([[1], [0, 2], [1]], 0)
        (2, 3, 2)
    """
    distancia = [-1] * len(vizinhos)
    distancia[origem] = 0
    fila = [origem]
    soma = 0
    for v in fila:
        proxima = distancia[v] + 1
        for w in vizinhos[v]:
            if distancia[w] < 0:
                distancia[w] = proxima
                soma += proxima
                fila.append(w)
    return distancia[fila[-1]], soma, len(fila) - 1


def _iniciar_processo(vizinhos: list[list[int]]) -> None:
    global _VIZINHOS
    _VIZINHOS = vizinhos


def _medir_bloco(origens: range) -> list[tuple[int, int, int]]:
    return [medir_origem(_VIZINHOS, o) for o in origens]


def calcular_distancias_exatas(
    adjacencia: Adjacencia, processos: int = 1
) -> DistanciasExatas:
    """
    :param adjacencia: grafo não dirigido e conexo
    :param processos: quantos processos dividem as n BFS (1 = no próprio processo)
    :return: diâmetro (maior excentricidade), raio (menor excentricidade), caminho médio
        (soma das distâncias sobre os n(n−1) pares ordenados) e os vértices do centro

    Exemplo:
        >>> d = calcular_distancias_exatas({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}})
        >>> d.diametro, d.raio, round(d.caminho_medio, 4), d.centro
        (2, 1, 1.3333, ['2'])
    """
    vertices, vizinhos = indexar(adjacencia)
    n = len(vertices)
    if processos <= 1:
        medidas = [medir_origem(vizinhos, o) for o in range(n)]
    else:
        tamanho = max(1, n // (processos * 8))
        blocos = [range(i, min(i + tamanho, n)) for i in range(0, n, tamanho)]
        with get_context("spawn").Pool(
            processos, initializer=_iniciar_processo, initargs=(vizinhos,)
        ) as pool:
            medidas = [m for bloco in pool.map(_medir_bloco, blocos) for m in bloco]
    if any(alcancados != n - 1 for _, _, alcancados in medidas):
        raise ValueError("o grafo não é conexo; use a maior componente")
    excentricidades = [e for e, _, _ in medidas]
    raio = min(excentricidades)
    return DistanciasExatas(
        diametro=max(excentricidades),
        raio=raio,
        caminho_medio=sum(s for _, s, _ in medidas) / (n * (n - 1)),
        pares=n * (n - 1),
        centro=[vertices[i] for i, e in enumerate(excentricidades) if e == raio],
    )
