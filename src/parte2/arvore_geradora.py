import heapq
from dataclasses import dataclass

from src.comum.tipos import AdjacenciaPonderada, ArestaJogos


@dataclass(frozen=True)
class ArvoreGeradora:
    """Arestas da árvore geradora mínima e a soma das distâncias"""

    arestas: list[ArestaJogos]
    custo_total: float


class ConjuntosDisjuntos:
    """Union-find com compressão de caminho e união por rank, base do Kruskal"""

    def __init__(self, elementos: list[str]) -> None:
        """
        :param elementos: cada um começa no próprio conjunto

        Exemplo:
            >>> ConjuntosDisjuntos(["a", "b"]).unir("a", "b")
            True
        """
        self.pai = {e: e for e in elementos}
        self.rank = {e: 0 for e in elementos}

    def encontrar(self, elemento: str) -> str:
        """
        :param elemento: elemento existente
        :return: representante do conjunto do elemento

        Exemplo:
            >>> ConjuntosDisjuntos(["a"]).encontrar("a")
            'a'
        """
        raiz = elemento
        while self.pai[raiz] != raiz:
            raiz = self.pai[raiz]
        while self.pai[elemento] != raiz:
            self.pai[elemento], elemento = raiz, self.pai[elemento]
        return raiz

    def unir(self, a: str, b: str) -> bool:
        """
        :param a: elemento existente
        :param b: elemento existente
        :return: False se já estavam no mesmo conjunto (a aresta fecharia um ciclo)

        Exemplo:
            >>> c = ConjuntosDisjuntos(["a", "b"]); c.unir("a", "b"), c.unir("b", "a")
            (True, False)
        """
        raiz_a, raiz_b = self.encontrar(a), self.encontrar(b)
        if raiz_a == raiz_b:
            return False
        if self.rank[raiz_a] < self.rank[raiz_b]:
            raiz_a, raiz_b = raiz_b, raiz_a
        self.pai[raiz_b] = raiz_a
        self.rank[raiz_a] += self.rank[raiz_a] == self.rank[raiz_b]
        return True


def calcular_kruskal(adjacencia: AdjacenciaPonderada) -> ArvoreGeradora:
    """
    :param adjacencia: grafo ponderado e conexo
    :return: ArvoreGeradora mínima, escolhendo arestas da mais leve para a mais pesada

    Exemplo:
        >>> calcular_kruskal({"a": {"b": 1.0, "c": 3.0}, "b": {"a": 1.0, "c": 1.0}, "c": {"a": 3.0, "b": 1.0}})
        ArvoreGeradora(arestas=[('a', 'b'), ('b', 'c')], custo_total=2.0)
    """
    arestas = sorted(
        (peso, u, v)
        for u, vizinhos in adjacencia.items()
        for v, peso in vizinhos.items()
        if u < v
    )
    conjuntos = ConjuntosDisjuntos(list(adjacencia))
    escolhidas: list[ArestaJogos] = []
    custo = 0.0
    for peso, u, v in arestas:
        if conjuntos.unir(u, v):
            escolhidas.append((u, v))
            custo += peso
    return ArvoreGeradora(escolhidas, custo)


def calcular_prim(adjacencia: AdjacenciaPonderada, origem: str) -> ArvoreGeradora:
    """
    :param adjacencia: grafo ponderado e conexo
    :param origem: vértice onde a árvore começa a crescer
    :return: ArvoreGeradora mínima, crescendo sempre pela aresta mais leve da fronteira

    Exemplo:
        >>> calcular_prim({"a": {"b": 1.0, "c": 3.0}, "b": {"a": 1.0, "c": 1.0}, "c": {"a": 3.0, "b": 1.0}}, "a")
        ArvoreGeradora(arestas=[('a', 'b'), ('b', 'c')], custo_total=2.0)
    """
    if origem not in adjacencia:
        raise KeyError(
            f"origem {origem!r} não está no grafo; esperado um vértice existente"
        )
    na_arvore = {origem}
    fronteira = [(peso, origem, v) for v, peso in adjacencia[origem].items()]
    heapq.heapify(fronteira)
    escolhidas: list[ArestaJogos] = []
    custo = 0.0
    while fronteira:
        peso, u, v = heapq.heappop(fronteira)
        if v in na_arvore:
            continue
        na_arvore.add(v)
        escolhidas.append((min(u, v), max(u, v)))
        custo += peso
        for w, peso_w in adjacencia[v].items():
            if w not in na_arvore:
                heapq.heappush(fronteira, (peso_w, v, w))
    return ArvoreGeradora(escolhidas, custo)
