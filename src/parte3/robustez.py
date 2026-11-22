import math
import random
from dataclasses import dataclass

from src.comum.grafo import componentes_conexas
from src.comum.tipos import Adjacencia
from src.parte1.topologia import estimar_caminho_medio

FRACAO_REMOVIDA: float = 0.05


@dataclass(frozen=True)
class MetricasRobustez:
    """Métricas A–D do Apêndice C, medidas no grafo que sobra após a remoção"""

    maior_componente: float  # A: S = |maior componente| / vértices restantes
    componentes: int  # B
    caminho_medio: float  # C: L estimado dentro da maior componente
    fracao_isolados: float  # D


def calcular_r(n: int, fracao: float = FRACAO_REMOVIDA) -> int:
    """
    :param n: vértices do grafo
    :param fracao: fração a remover
    :return: r = ⌈fracao · n⌉

    Exemplo:
        >>> calcular_r(21284)
        1065
    """
    return math.ceil(fracao * n)


def remover_vertices(adjacencia: Adjacencia, removidos: set[str]) -> Adjacencia:
    """
    :param adjacencia: grafo não dirigido
    :param removidos: vértices a tirar, junto com as arestas incidentes
    :return: nova adjacência; vértices que perderam todos os vizinhos ficam, isolados

    Exemplo:
        >>> remover_vertices({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, {"2"})
        {'1': set(), '3': set()}
    """
    return {
        v: vizinhos - removidos
        for v, vizinhos in adjacencia.items()
        if v not in removidos
    }


def medir_robustez(
    adjacencia: Adjacencia, n_origens: int, semente: int
) -> MetricasRobustez:
    """
    :param adjacencia: grafo após a remoção
    :param n_origens: origens sorteadas para estimar L na maior componente
    :param semente: SEED do sorteio das origens
    :return: MetricasRobustez (A, B, C e D)

    Exemplo:
        >>> medir_robustez({"1": {"2"}, "2": {"1"}, "3": set(), "4": set()}, 2, 42)
        MetricasRobustez(maior_componente=0.5, componentes=3, caminho_medio=1.0, fracao_isolados=0.5)
    """
    componentes = componentes_conexas(adjacencia)
    maior = componentes[0]
    restrita = {v: adjacencia[v] for v in maior}
    n = len(adjacencia)
    return MetricasRobustez(
        maior_componente=len(maior) / n,
        componentes=len(componentes),
        caminho_medio=estimar_caminho_medio(restrita, min(n_origens, len(maior)), semente).media,
        fracao_isolados=sum(1 for v in adjacencia.values() if not v) / n,
    )


def remover_ao_acaso(
    adjacencia: Adjacencia, r: int, repeticoes: int, n_origens: int, semente: int
) -> list[MetricasRobustez]:
    """
    :param adjacencia: grafo original
    :param r: vértices removidos por repetição
    :param repeticoes: T, sorteios independentes para reduzir sorte ou azar
    :param n_origens: origens para L em cada repetição
    :param semente: SEED; a repetição t usa um sorteio derivado dela
    :return: uma MetricasRobustez por repetição

    Exemplo:
        >>> len(remover_ao_acaso({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, 1, 3, 2, 42))
        3
    """
    sorteio = random.Random(semente)
    vertices = sorted(adjacencia)
    resultados = []
    for _ in range(repeticoes):
        removidos = set(sorteio.sample(vertices, r))
        restante = remover_vertices(adjacencia, removidos)
        resultados.append(medir_robustez(restante, n_origens, sorteio.randrange(2**32)))
    return resultados


def ordenar_por_centralidade(centralidade: dict[str, float]) -> list[str]:
    """
    :param centralidade: valor de centralidade de cada vértice
    :return: ranking fixo, do mais central para o menos; empates pelo rótulo, para ser determinístico

    Exemplo:
        >>> ordenar_por_centralidade({"a": 1, "b": 3, "c": 1})
        ['b', 'a', 'c']
    """
    return sorted(centralidade, key=lambda v: (-centralidade[v], v))


def medir_curva_de_ataque(
    adjacencia: Adjacencia, ranking: list[str], fracoes: list[float]
) -> list[float]:
    """
    :param adjacencia: grafo original
    :param ranking: ordem de remoção (fixa)
    :param fracoes: frações f de vértices removidos
    :return: S(f), a fração dos restantes que fica na maior componente, para cada f

    Exemplo:
        >>> medir_curva_de_ataque({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, ["2", "1", "3"], [0.0, 0.33])
        [1.0, 0.5]
    """
    curva = []
    for fracao in fracoes:
        removidos = set(ranking[: calcular_r(len(adjacencia), fracao)])
        restante = remover_vertices(adjacencia, removidos)
        curva.append(len(componentes_conexas(restante)[0]) / len(restante))
    return curva
