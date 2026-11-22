from collections import Counter

from src.comum.tipos import Jogo, PesosArestas


def medir_mistura_de_plataformas(
    pesos: PesosArestas, jogos: dict[str, Jogo]
) -> tuple[float, float]:
    """
    :param pesos: arestas do grafo
    :param jogos: catálogo com a plataforma de cada vértice
    :return: (observada, esperada): fração de arestas entre jogos da mesma plataforma, e a
        fração esperada se as pontas fossem ligadas ao acaso, Σ_p (s_p / 2m)², com s_p as pontas de p

    Exemplo:
        >>> j = {v: Jogo(v, v, p, "") for v, p in [("a", "PS4"), ("b", "PS4"), ("c", "PC"), ("d", "PC")]}
        >>> medir_mistura_de_plataformas({("a", "b"): 2, ("c", "d"): 2}, j)
        (1.0, 0.5)
    """
    mesma = 0
    pontas: Counter[str] = Counter()
    for p, q in pesos:
        plataforma_p, plataforma_q = jogos[p].plataforma, jogos[q].plataforma
        mesma += plataforma_p == plataforma_q
        pontas[plataforma_p] += 1
        pontas[plataforma_q] += 1
    total = 2 * len(pesos)
    esperada = sum((s / total) ** 2 for s in pontas.values())
    return mesma / len(pesos), esperada


def resumir_plataformas(
    componente: set[str], jogos: dict[str, Jogo], quantas: int
) -> list[tuple[str, int]]:
    """
    :param componente: vértices de uma componente
    :param jogos: catálogo com a plataforma de cada vértice
    :param quantas: quantas plataformas listar
    :return: plataformas mais frequentes na componente, com a contagem

    Exemplo:
        >>> j = {v: Jogo(v, v, p, "") for v, p in [("a", "PS4"), ("b", "PS4"), ("c", "PC")]}
        >>> resumir_plataformas({"a", "b", "c"}, j, 1)
        [('PS4', 2)]
    """
    return Counter(jogos[v].plataforma for v in componente).most_common(quantas)
