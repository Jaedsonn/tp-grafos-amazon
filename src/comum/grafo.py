from collections import Counter, deque
from collections.abc import Iterable

from src.comum.tipos import Adjacencia, AdjacenciaPonderada, ArestaJogos, PesosArestas


def montar_adjacencia_ponderada(pesos: PesosArestas) -> AdjacenciaPonderada:
    """
    :param pesos: arestas {(p, q): w}
    :return: adjacência com distância d = 1/w (T7): mais usuários em comum, mais perto

    Exemplo:
        >>> montar_adjacencia_ponderada({("1", "2"): 4})
        {'1': {'2': 0.25}, '2': {'1': 0.25}}
    """
    adjacencia: AdjacenciaPonderada = {}
    for (p, q), peso in pesos.items():
        adjacencia.setdefault(p, {})[q] = 1 / peso
        adjacencia.setdefault(q, {})[p] = 1 / peso
    return adjacencia


def montar_adjacencia(arestas: Iterable[ArestaJogos]) -> Adjacencia:
    """
    :param arestas: pares (p, q)
    :return: mapa vértice -> vizinhos

    Exemplo:
        >>> montar_adjacencia([("1", "2")])
        {'1': {'2'}, '2': {'1'}}
    """
    adjacencia: Adjacencia = {}
    for p, q in arestas:
        adjacencia.setdefault(p, set()).add(q)
        adjacencia.setdefault(q, set()).add(p)
    return adjacencia


def visitar_em_largura(adjacencia: Adjacencia, origem: str) -> list[str]:
    """
    :param adjacencia: grafo não dirigido
    :param origem: vértice inicial, presente em adjacencia
    :return: vértices alcançáveis, começando pela origem

    Exemplo:
        >>> visitar_em_largura({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, "1")
        ['1', '2', '3']
    """
    if origem not in adjacencia:
        raise KeyError(
            f"origem {origem!r} não está no grafo; esperado um vértice existente"
        )
    visitados = {origem}
    ordem = [origem]
    fila = deque([origem])
    while fila:
        for vizinho in sorted(adjacencia[fila.popleft()]):
            if vizinho in visitados:
                continue
            visitados.add(vizinho)
            ordem.append(vizinho)
            fila.append(vizinho)
    return ordem


def componentes_conexas(adjacencia: Adjacencia) -> list[set[str]]:
    """
    :param adjacencia: grafo não dirigido
    :return: lista de conjuntos de vértices

    Exemplo:
        >>> [len(c) for c in componentes_conexas({"1": {"2"}, "2": {"1"}, "3": set()})]
        [2, 1]
    """
    vistos: set[str] = set()
    componentes: list[set[str]] = []
    for vertice in sorted(adjacencia):
        if vertice in vistos:
            continue
        componente = set(visitar_em_largura(adjacencia, vertice))
        vistos |= componente
        componentes.append(componente)
    return sorted(componentes, key=len, reverse=True)


def contar_tamanhos_componentes(
    adjacencia: Adjacencia, vertices: set[str]
) -> dict[int, int]:
    """
    :param adjacencia: grafo não dirigido, só com vértices que têm aresta
    :param vertices: conjunto completo de vértices; os ausentes da adjacência são isolados
    :return: mapa tamanho da componente -> quantidade, do maior tamanho para o menor

    Exemplo:
        >>> contar_tamanhos_componentes({"1": {"2"}, "2": {"1"}}, {"1", "2", "3", "4"})
        {2: 1, 1: 2}
    """
    tamanhos = Counter(len(c) for c in componentes_conexas(adjacencia))
    # isolados não aparecem na adjacência, mas são componentes de tamanho 1 de G = (P, E)
    isolados = len(vertices - adjacencia.keys())
    if isolados:
        tamanhos[1] += isolados
    return dict(sorted(tamanhos.items(), reverse=True))


def distancias_em_largura(adjacencia: Adjacencia, origem: str) -> dict[str, int]:
    """
    :param adjacencia: grafo não dirigido
    :param origem: vértice inicial, presente em adjacencia
    :return: distância em saltos da origem até cada vértice alcançável

    Exemplo:
        >>> distancias_em_largura({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, "1")
        {'1': 0, '2': 1, '3': 2}
    """
    if origem not in adjacencia:
        raise KeyError(
            f"origem {origem!r} não está no grafo; esperado um vértice existente"
        )
    distancias = {origem: 0}
    fila = deque([origem])
    while fila:
        atual = fila.popleft()
        for vizinho in adjacencia[atual]:
            if vizinho not in distancias:
                distancias[vizinho] = distancias[atual] + 1
                fila.append(vizinho)
    return distancias


def amostrar_bola_de_neve(
    adjacencia: Adjacencia, origem: str, tamanho: int
) -> set[str]:
    """
    :param adjacencia: grafo não dirigido
    :param origem: vértice onde a bola de neve começa
    :param tamanho: número de vértices desejado
    :return: os primeiros vértices da BFS, que induzem um subgrafo conexo

    Exemplo:
        >>> sorted(amostrar_bola_de_neve({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, "1", 2))
        ['1', '2']
    """
    # sortear vértices soltos daria um subgrafo desconexo; a BFS preserva a conexidade
    return set(visitar_em_largura(adjacencia, origem)[:tamanho])


def restringir_arestas(pesos: PesosArestas, vertices: set[str]) -> PesosArestas:
    """
    :param pesos: arestas com peso
    :param vertices: vértices a manter
    :return: subgrafo induzido, com os mesmos pesos

    Exemplo:
        >>> restringir_arestas({("1", "2"): 2, ("3", "4"): 5}, {"1", "2"})
        {('1', '2'): 2}
    """
    return {(p, q): w for (p, q), w in pesos.items() if p in vertices and q in vertices}
