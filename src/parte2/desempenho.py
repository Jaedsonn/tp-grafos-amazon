import gc
import math
import os
import platform
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass

import igraph
import networkx as nx
import numpy as np

from src.comum.estatistica import Estimativa, estimar_media_com_ic
from src.comum.grafo import (
    amostrar_bola_de_neve,
    montar_adjacencia,
    montar_adjacencia_ponderada,
    restringir_arestas,
)
from src.comum.tipos import Adjacencia, AdjacenciaPonderada, PesosArestas

REPETICOES: int = 30
AQUECIMENTOS: int = 2


def cronometrar(
    executar: Callable[[], object],
    repeticoes: int = REPETICOES,
    aquecimentos: int = AQUECIMENTOS,
) -> Estimativa:
    """
    :param executar: chamada sem argumentos que roda o algoritmo uma vez
    :param repeticoes: execuções medidas (30 => IC pela normal, z = 1,96)
    :param aquecimentos: execuções descartadas, para aquecer caches e alocador
    :return: Estimativa do tempo em segundos (média, DP e IC 95%)

    Exemplo:
        >>> cronometrar(lambda: sum(range(100)), repeticoes=3, aquecimentos=1).n
        3
    """
    for _ in range(aquecimentos):
        executar()
    tempos = []
    for _ in range(repeticoes):
        gc.collect()
        inicio = time.perf_counter()
        executar()
        tempos.append(time.perf_counter() - inicio)
    return estimar_media_com_ic(tempos)


def ajustar_inclinacao(custos: list[float], tempos: list[float]) -> float:
    """
    :param custos: custo teórico de cada tamanho (ex.: n + m, m·log n, n³)
    :param tempos: tempo médio observado em cada tamanho
    :return: inclinação da reta log(tempo) × log(custo); perto de 1 confirma a complexidade

    Exemplo:
        >>> round(ajustar_inclinacao([10, 100, 1000], [1, 100, 10000]), 3)
        2.0
    """
    if len(custos) != len(tempos) or len(custos) < 2:
        raise ValueError(
            f"custos={custos!r}, tempos={tempos!r}; esperado duas listas de mesmo tamanho >= 2"
        )
    inclinacao, _ = np.polyfit(np.log(custos), np.log(tempos), 1)
    return float(inclinacao)


def custo_linear(n: int, m: int) -> float:
    """
    :param n: vértices
    :param m: arestas
    :return: n + m, custo de BFS, DFS, Euler e Tarjan

    Exemplo:
        >>> custo_linear(3, 2)
        5
    """
    return n + m


def custo_heap(n: int, m: int) -> float:
    """
    :param n: vértices
    :param m: arestas
    :return: m·log n, custo de Dijkstra, Prim e Kruskal com heap ou ordenação

    Exemplo:
        >>> round(custo_heap(math.e ** 2, 10), 6)
        20.0
    """
    return m * math.log(n)


@dataclass(frozen=True)
class Subgrafo:
    """Subgrafo conexo induzido por bola de neve, pronto para os algoritmos"""

    adjacencia: Adjacencia
    adjacencia_ponderada: AdjacenciaPonderada
    origem: str
    n: int
    m: int


@dataclass(frozen=True)
class PontoEscalabilidade:
    """Tempo de um algoritmo num tamanho de subgrafo"""

    algoritmo: str
    n: int
    m: int
    tempo: Estimativa


def induzir_bola_de_neve(
    pesos: PesosArestas, adjacencia: Adjacencia, origem: str, tamanho: int
) -> Subgrafo:
    """
    :param pesos: arestas do grafo completo
    :param adjacencia: adjacência do grafo completo
    :param origem: vértice onde a bola de neve começa (e origem das buscas)
    :param tamanho: nº de vértices; use len(adjacencia) para o grafo inteiro
    :return: Subgrafo conexo com n vértices e as m arestas induzidas

    Exemplo:
        >>> s = induzir_bola_de_neve({("1", "2"): 2, ("2", "3"): 1}, {"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, "1", 2)
        >>> s.n, s.m
        (2, 1)
    """
    sub = restringir_arestas(pesos, amostrar_bola_de_neve(adjacencia, origem, tamanho))
    adjacencia_sub = montar_adjacencia(sub)
    return Subgrafo(
        adjacencia_sub,
        montar_adjacencia_ponderada(sub),
        origem,
        len(adjacencia_sub),
        len(sub),
    )


def medir_escalabilidade(
    subgrafos: list[Subgrafo], algoritmos: dict[str, Callable[[Subgrafo], object]]
) -> list[PontoEscalabilidade]:
    """
    :param subgrafos: tamanhos crescentes do mesmo grafo
    :param algoritmos: nome -> chamada que roda o algoritmo num Subgrafo
    :return: um PontoEscalabilidade por (algoritmo, subgrafo), com 30 repetições cada

    Exemplo:
        pontos = medir_escalabilidade(subgrafos, {"BFS": lambda s: distancias_em_largura(s.adjacencia, s.origem)})
    """
    pontos = []
    for subgrafo in subgrafos:
        for nome, executar in algoritmos.items():
            tempo = cronometrar(lambda: executar(subgrafo))
            pontos.append(PontoEscalabilidade(nome, subgrafo.n, subgrafo.m, tempo))
    return pontos


def descrever_ambiente() -> dict[str, str]:
    """
    :return: hardware e versões, que o relatório precisa citar junto dos tempos

    Exemplo:
        >>> "python" in descrever_ambiente()
        True
    """
    with open("/proc/meminfo", encoding="utf-8") as fluxo:
        memoria_kb = int(fluxo.readline().split()[1])
    return {
        "cpu": ler_modelo_cpu(),
        "nucleos": str(os.cpu_count()),
        "ram_gb": f"{memoria_kb / 1024**2:.1f}",
        "sistema": platform.platform(),
        "python": sys.version.split()[0],
        "networkx": nx.__version__,
        "igraph": igraph.__version__,
        "numpy": np.__version__,
    }


def ler_modelo_cpu() -> str:
    """
    :return: o "model name" de /proc/cpuinfo; platform.processor() no Linux só diz "x86_64"

    Exemplo:
        >>> isinstance(ler_modelo_cpu(), str)
        True
    """
    with open("/proc/cpuinfo", encoding="utf-8") as fluxo:
        for linha in fluxo:
            if linha.startswith("model name"):
                return linha.split(":", 1)[1].strip()
    return platform.machine()
