import math
import random
import statistics
from dataclasses import dataclass

from src.comum.grafo import montar_adjacencia
from src.comum.tipos import Adjacencia, ParAvaliacao
from src.parte1.topologia import (
    calcular_clusterizacao_local,
    contar_triangulos_por_vertice,
    estimar_caminho_medio,
)


@dataclass(frozen=True)
class MedidasPequenoMundo:
    """C e L de um grafo, as duas medidas da definição do Apêndice A"""

    n: int
    m: int
    clusterizacao: float
    caminho_medio: float


def medir_pequeno_mundo(
    adjacencia: Adjacencia, n_origens: int, semente: int
) -> MedidasPequenoMundo:
    """
    :param adjacencia: grafo não dirigido e conexo
    :param n_origens: origens sorteadas para estimar L por BFS
    :param semente: SEED do sorteio das origens
    :return: MedidasPequenoMundo com C médio e L estimado

    Exemplo:
        >>> medir_pequeno_mundo({"1": {"2", "3"}, "2": {"1", "3"}, "3": {"1", "2"}}, 3, 42)
        MedidasPequenoMundo(n=3, m=3, clusterizacao=1.0, caminho_medio=1.0)
    """
    triangulos = contar_triangulos_por_vertice(adjacencia)
    clusterizacao = calcular_clusterizacao_local(adjacencia, triangulos)
    n_origens = min(n_origens, len(adjacencia))
    return MedidasPequenoMundo(
        n=len(adjacencia),
        m=sum(len(v) for v in adjacencia.values()) // 2,
        clusterizacao=statistics.fmean(clusterizacao.values()),
        caminho_medio=estimar_caminho_medio(adjacencia, n_origens, semente).media,
    )


def gerar_erdos_renyi(n: int, m: int, semente: int) -> Adjacencia:
    """
    :param n: vértices, rotulados "0" … "n-1"
    :param m: arestas distintas, sorteadas uniformemente entre os n(n−1)/2 pares (G(n, m))
    :param semente: SEED do sorteio
    :return: adjacência do grafo aleatório com o mesmo n e o mesmo grau médio do original

    Exemplo:
        >>> g = gerar_erdos_renyi(10, 15, 42)
        >>> len(g), sum(len(v) for v in g.values()) // 2
        (10, 15)
    """
    if m > n * (n - 1) // 2:
        raise ValueError(f"m = {m} > n(n−1)/2 = {n * (n - 1) // 2}; esperado um grafo simples")
    sorteio = random.Random(semente)
    arestas: set[tuple[str, str]] = set()
    while len(arestas) < m:
        p, q = sorteio.randrange(n), sorteio.randrange(n)
        if p != q:
            arestas.add((str(min(p, q)), str(max(p, q))))
    adjacencia = montar_adjacencia(arestas)
    for v in range(n):
        adjacencia.setdefault(str(v), set())
    return adjacencia


def calcular_referencia_analitica(n: int, grau_medio: float) -> tuple[float, float]:
    """
    :param n: vértices
    :param grau_medio: ⟨k⟩ = 2m/n
    :return: (C_rand, L_rand) ≈ (⟨k⟩/(n−1), ln n / ln⟨k⟩) do Erdős–Rényi

    Exemplo:
        >>> c, l = calcular_referencia_analitica(1001, 10.0)
        >>> round(c, 4), round(l, 2)
        (0.01, 3.0)
    """
    return grau_medio / (n - 1), math.log(n) / math.log(grau_medio)


def calcular_sigma(
    grafo: MedidasPequenoMundo, aleatorio: MedidasPequenoMundo
) -> float:
    """
    :param grafo: medidas do grafo real
    :param aleatorio: medidas do modelo nulo
    :return: σ = (C/C_rand) / (L/L_rand); σ ≫ 1 indica small-world

    Exemplo:
        >>> calcular_sigma(MedidasPequenoMundo(1, 1, 0.3, 4.0), MedidasPequenoMundo(1, 1, 0.003, 3.0))
        75.0
    """
    razao_c = grafo.clusterizacao / aleatorio.clusterizacao
    razao_l = grafo.caminho_medio / aleatorio.caminho_medio
    return razao_c / razao_l


def embaralhar_bipartido(
    pares: list[ParAvaliacao], semente: int
) -> list[ParAvaliacao]:
    """
    :param pares: arestas (usuário, jogo) já tratadas (T1–T3)
    :param semente: SEED da permutação
    :return: bipartido aleatório que preserva todos os k_u e k_p (modelo de configuração
        bipartido); pares repetidos que a permutação cria são descartados

    Exemplo:
        >>> embaralhados = embaralhar_bipartido([("u", "a"), ("u", "b"), ("v", "c")], 42)
        >>> sorted(u for u, _ in embaralhados), sorted(p for _, p in embaralhados)
        (['u', 'u', 'v'], ['a', 'b', 'c'])
    """
    jogos = [jogo for _, jogo in pares]
    # permutar só o lado dos jogos mantém quantas pontas cada usuário e cada jogo têm
    random.Random(semente).shuffle(jogos)
    return list(dict.fromkeys(zip((u for u, _ in pares), jogos)))
