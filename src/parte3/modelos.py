"""
Geradores dos modelos clássicos da Q5, com código próprio.

O Erdős–Rényi G(n, m) já está em ``pequeno_mundo.py``; aqui ficam o Barabási–Albert e o
Watts–Strogatz. Os vértices são rotulados "0" … "n-1", como no G(n, m).
"""

import random

from src.comum.tipos import Adjacencia


def gerar_barabasi_albert(n: int, m_novo: int, semente: int) -> Adjacencia:
    """
    Ligação preferencial (Barabási e Albert, 1999). Começa com um clique de m_novo + 1
    vértices; cada vértice novo se liga a m_novo vértices distintos, sorteados com
    probabilidade proporcional ao grau. A lista ``pontas`` repete cada vértice uma vez por
    aresta incidente, então um sorteio uniforme nela é um sorteio proporcional ao grau.

    :param n: vértices
    :param m_novo: arestas de cada vértice novo
    :param semente: SEED do sorteio
    :return: adjacência com C(m_novo + 1, 2) + (n − m_novo − 1)·m_novo arestas

    Exemplo:
        >>> g = gerar_barabasi_albert(100, 3, 42)
        >>> len(g), sum(len(v) for v in g.values()) // 2, min(len(v) for v in g.values())
        (100, 294, 3)
    """
    if not 1 <= m_novo < n:
        raise ValueError(
            f"esperado 1 ≤ m_novo < n; recebido m_novo = {m_novo}, n = {n}"
        )
    sorteio = random.Random(semente)
    adjacencia: Adjacencia = {str(v): set() for v in range(n)}
    pontas: list[int] = []
    for p in range(m_novo + 1):
        for q in range(p + 1, m_novo + 1):
            adjacencia[str(p)].add(str(q))
            adjacencia[str(q)].add(str(p))
            pontas += [p, q]
    for novo in range(m_novo + 1, n):
        alvos: set[int] = set()
        while len(alvos) < m_novo:
            alvos.add(pontas[sorteio.randrange(len(pontas))])
        for alvo in alvos:
            adjacencia[str(novo)].add(str(alvo))
            adjacencia[str(alvo)].add(str(novo))
            pontas += [novo, alvo]
    return adjacencia


def gerar_watts_strogatz(n: int, k: int, p: float, semente: int) -> Adjacencia:
    """
    Anel religado (Watts e Strogatz, 1998). Cada vértice começa ligado aos k/2 vizinhos de
    cada lado; depois, cada aresta (i, i + j) é religada com probabilidade p para um destino
    uniforme, sem criar laço nem aresta repetida. O número de arestas fica n·k/2.

    :param n: vértices
    :param k: grau inicial, par
    :param p: probabilidade de religar cada aresta
    :param semente: SEED do sorteio
    :return: adjacência do grafo religado

    Exemplo:
        >>> g = gerar_watts_strogatz(20, 4, 0.0, 42)
        >>> sorted(g["0"], key=int), sum(len(v) for v in g.values()) // 2
        (['1', '2', '18', '19'], 40)
    """
    if k % 2 or not 0 < k < n:
        raise ValueError(f"esperado k par com 0 < k < n; recebido k = {k}")
    sorteio = random.Random(semente)
    adjacencia: Adjacencia = {str(v): set() for v in range(n)}
    for v in range(n):
        for j in range(1, k // 2 + 1):
            w = (v + j) % n
            adjacencia[str(v)].add(str(w))
            adjacencia[str(w)].add(str(v))
    for j in range(1, k // 2 + 1):
        for v in range(n):
            w = str((v + j) % n)
            if sorteio.random() >= p or w not in adjacencia[str(v)]:
                continue
            if len(adjacencia[str(v)]) >= n - 1:
                continue
            novo = str(sorteio.randrange(n))
            while novo == str(v) or novo in adjacencia[str(v)]:
                novo = str(sorteio.randrange(n))
            adjacencia[str(v)].discard(w)
            adjacencia[w].discard(str(v))
            adjacencia[str(v)].add(novo)
            adjacencia[novo].add(str(v))
    return adjacencia
