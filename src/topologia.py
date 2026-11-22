import random
import statistics
from collections import Counter
from dataclasses import dataclass

from src.estatistica import Estimativa, estimar_media_com_ic
from src.grafo import distancias_em_largura
from src.tipos import Adjacencia, PesosArestas


@dataclass(frozen=True)
class ResumoGraus:
    """Mínimo, máximo e média de uma sequência de graus ou forças"""

    minimo: int
    maximo: int
    media: float


def calcular_graus(adjacencia: Adjacencia) -> dict[str, int]:
    """
    :param adjacencia: grafo não dirigido
    :return: grau k_v de cada vértice

    Exemplo:
        >>> calcular_graus({"1": {"2", "3"}, "2": {"1"}, "3": {"1"}})
        {'1': 2, '2': 1, '3': 1}
    """
    return {vertice: len(vizinhos) for vertice, vizinhos in adjacencia.items()}


def calcular_forcas(pesos: PesosArestas) -> dict[str, int]:
    """
    :param pesos: arestas {(p, q): w}
    :return: força s(v) = Σ w das arestas incidentes, o grau ponderado

    Exemplo:
        >>> calcular_forcas({("1", "2"): 3, ("2", "3"): 1})
        {'1': 3, '2': 4, '3': 1}
    """
    forcas: Counter[str] = Counter()
    for (p, q), peso in pesos.items():
        forcas[p] += peso
        forcas[q] += peso
    return dict(forcas)


def resumir_graus(valores: dict[str, int]) -> ResumoGraus:
    """
    :param valores: grau (ou força) por vértice, não vazio
    :return: ResumoGraus

    Exemplo:
        >>> resumir_graus({"1": 2, "2": 1, "3": 3})
        ResumoGraus(minimo=1, maximo=3, media=2.0)
    """
    if not valores:
        raise ValueError("sequência de graus vazia; esperado ao menos um vértice")
    sequencia = list(valores.values())
    return ResumoGraus(min(sequencia), max(sequencia), statistics.fmean(sequencia))


def distribuir_graus(graus: dict[str, int]) -> dict[int, int]:
    """
    :param graus: grau por vértice
    :return: histograma k -> nº de vértices com grau k, em ordem crescente de k

    Exemplo:
        >>> distribuir_graus({"1": 2, "2": 1, "3": 1})
        {1: 2, 2: 1}
    """
    return dict(sorted(Counter(graus.values()).items()))


def calcular_ccdf(distribuicao: dict[int, int]) -> dict[int, float]:
    """
    :param distribuicao: histograma k -> quantidade
    :return: P(K >= k) para cada k observado; é mais estável que o histograma na cauda

    Exemplo:
        >>> calcular_ccdf({1: 2, 2: 1, 4: 1})
        {1: 1.0, 2: 0.5, 4: 0.25}
    """
    total = sum(distribuicao.values())
    restantes = total
    ccdf: dict[int, float] = {}
    for grau in sorted(distribuicao):
        ccdf[grau] = restantes / total
        restantes -= distribuicao[grau]
    return ccdf


def calcular_densidade(n: int, m: int) -> float:
    """
    :param n: número de vértices
    :param m: número de arestas
    :return: 2m / (n(n − 1)), fração dos pares possíveis que são arestas

    Exemplo:
        >>> calcular_densidade(4, 3)
        0.5
    """
    if n < 2:
        raise ValueError(f"n = {n}; esperado ao menos 2 vértices para a densidade")
    return 2 * m / (n * (n - 1))


def contar_triangulos_por_vertice(adjacencia: Adjacencia) -> dict[str, int]:
    """
    :param adjacencia: grafo não dirigido
    :return: t(v), nº de triângulos que contêm v (arestas entre vizinhos de v)

    Exemplo:
        >>> contar_triangulos_por_vertice({"1": {"2", "3"}, "2": {"1", "3"}, "3": {"1", "2"}})
        {'1': 1, '2': 1, '3': 1}
    """
    # cada aresta {u, w} entre vizinhos de v aparece duas vezes (a partir de u e de w)
    return {
        v: sum(len(vizinhos & adjacencia[u]) for u in vizinhos) // 2
        for v, vizinhos in adjacencia.items()
    }


def calcular_clusterizacao_local(
    adjacencia: Adjacencia, triangulos: dict[str, int]
) -> dict[str, float]:
    """
    :param adjacencia: grafo não dirigido
    :param triangulos: t(v) de cada vértice
    :return: C_v = 2t(v) / (k_v(k_v − 1)), com C_v = 0 se k_v < 2 (mesma convenção do networkx)

    Exemplo:
        >>> calcular_clusterizacao_local({"1": {"2", "3"}, "2": {"1"}, "3": {"1"}}, {"1": 0, "2": 0, "3": 0})
        {'1': 0.0, '2': 0.0, '3': 0.0}
    """
    clusterizacao: dict[str, float] = {}
    for v, vizinhos in adjacencia.items():
        k = len(vizinhos)
        clusterizacao[v] = 2 * triangulos[v] / (k * (k - 1)) if k >= 2 else 0.0
    return clusterizacao


def estimar_caminho_medio(
    adjacencia: Adjacencia, n_origens: int, semente: int
) -> Estimativa:
    """
    :param adjacencia: grafo não dirigido e conexo
    :param n_origens: quantas origens sortear para as BFS
    :param semente: SEED, para a amostra ser reprodutível
    :return: Estimativa de L, a média das distâncias médias a partir de cada origem

    Exemplo:
        >>> caminho = {"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}
        >>> round(estimar_caminho_medio(caminho, 3, 42).media, 4)
        1.3333
    """
    # num grafo conexo cada origem alcança os mesmos n − 1 alvos, então a média
    # das médias por origem é um estimador não viesado de L
    origens = random.Random(semente).sample(sorted(adjacencia), n_origens)
    medias = []
    for origem in origens:
        distancias = distancias_em_largura(adjacencia, origem)
        medias.append(sum(distancias.values()) / (len(distancias) - 1))
    return estimar_media_com_ic(medias)
