from collections import Counter, defaultdict
from collections.abc import Iterable
from itertools import combinations

from src.comum.tipos import ArestaJogos, EtapaFunil, ParAvaliacao, PesosArestas


def agrupar_por_usuario(pares: Iterable[ParAvaliacao]) -> dict[str, list[str]]:
    """
    :param pares: arestas únicas do bipartido
    :return: mapa usuário -> jogos avaliados

    Exemplo:
        >>> agrupar_por_usuario([("u", "a"), ("u", "b")])
        {'u': ['a', 'b']}
    """
    jogos_por_usuario: defaultdict[str, list[str]] = defaultdict(list)
    for usuario, jogo in pares:
        jogos_por_usuario[usuario].append(jogo)
    return dict(jogos_por_usuario)


def projetar_coavaliacao(
    jogos_por_usuario: dict[str, list[str]],
) -> Counter[ArestaJogos]:
    """
    :param jogos_por_usuario: mapa usuário -> jogos avaliados (sem repetição)
    :return: contador {(p, q): w} com p < q, onde w = |N(p) ∩ N(q)|

    Exemplo:
        >>> projetar_coavaliacao({"a": ["1", "2", "3"], "b": ["2", "3"]})[("2", "3")]
        2
    """
    pesos: Counter[ArestaJogos] = Counter()
    for jogos in jogos_por_usuario.values():
        # sorted garante a chave canônica (p < q), sem precisar deduplicar depois
        pesos.update(combinations(sorted(jogos), 2))
    return pesos


def podar_arestas_fracas(pesos: Counter[ArestaJogos], minimo: int) -> PesosArestas:
    """
    :param pesos: arestas da projeção com seus pesos
    :param minimo: menor peso aceito
    :return: backbone {(p, q): w}

    Exemplo:
        >>> podar_arestas_fracas(Counter({("1", "2"): 1, ("2", "3"): 2}), minimo=2)
        {('2', '3'): 2}
    """
    return {aresta: peso for aresta, peso in pesos.items() if peso >= minimo}


def resumir_projecao(
    nome: str, pesos: PesosArestas | Counter[ArestaJogos]
) -> EtapaFunil:
    """
    :param nome: rótulo do passo, ex.: "5_backbone"
    :param pesos: arestas do grafo jogo–jogo naquele passo
    :return: EtapaFunil com usuarios=None, pois os usuários já viraram arestas

    Exemplo:
        >>> resumir_projecao("x", {("1", "2"): 2, ("2", "3"): 2})
        EtapaFunil(nome='x', usuarios=None, jogos=3, arestas=2)
    """
    vertices = {vertice for aresta in pesos for vertice in aresta}
    return EtapaFunil(nome, None, len(vertices), len(pesos))
