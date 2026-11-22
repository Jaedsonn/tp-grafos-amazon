from collections import Counter
from collections.abc import Iterable

from src.tipos import EtapaFunil, ParAvaliacao

LADO_USUARIO: int = 0
LADO_JOGO: int = 1


def deduplicar(pares: Iterable[ParAvaliacao]) -> list[ParAvaliacao]:
    """
    :param pares: arestas do bipartido, possivelmente repetidas
    :return: arestas únicas, na ordem da primeira ocorrência (reprodutível)

    Exemplo:
        >>> deduplicar([("u", "j"), ("u", "j"), ("v", "j")])
        [('u', 'j'), ('v', 'j')]
    """
    return list(dict.fromkeys(pares))


def contar_graus(pares: Iterable[ParAvaliacao], lado: int) -> Counter[str]:
    """
    :param pares: arestas únicas do bipartido
    :param lado: LADO_USUARIO (k_u) ou LADO_JOGO (k_p)
    :return: contador vértice -> grau

    Exemplo:
        >>> contar_graus([("u", "j1"), ("u", "j2")], LADO_USUARIO)["u"]
        2
    """
    return Counter(par[lado] for par in pares)


def filtrar_usuarios_vorazes(pares: list[ParAvaliacao], cap: int) -> list[ParAvaliacao]:
    """
    :param pares: arestas únicas do bipartido
    :param cap: maior k_u aceito
    :return: arestas dos usuários mantidos

    Exemplo:
        >>> filtrar_usuarios_vorazes([("u", "a"), ("u", "b"), ("v", "a")], cap=1)
        [('v', 'a')]
    """
    graus = contar_graus(pares, LADO_USUARIO)
    return [par for par in pares if graus[par[LADO_USUARIO]] <= cap]


def filtrar_jogos_raros(pares: list[ParAvaliacao], minimo: int) -> list[ParAvaliacao]:
    """
    :param pares: arestas do bipartido após T2
    :param minimo: menor k_p aceito
    :return: arestas dos jogos mantidos

    Exemplo:
        >>> filtrar_jogos_raros([("u", "a"), ("v", "a"), ("u", "b")], minimo=2)
        [('u', 'a'), ('v', 'a')]
    """
    graus = contar_graus(pares, LADO_JOGO)
    return [par for par in pares if graus[par[LADO_JOGO]] >= minimo]


def resumir_bipartido(nome: str, pares: list[ParAvaliacao]) -> EtapaFunil:
    """
    :param nome: rótulo do passo, ex.: "1_dedup"
    :param pares: arestas do bipartido naquele passo
    :return: EtapaFunil com os três tamanhos

    Exemplo:
        >>> resumir_bipartido("x", [("u", "a"), ("v", "a")])
        EtapaFunil(nome='x', usuarios=2, jogos=1, arestas=2)
    """
    usuarios = {par[LADO_USUARIO] for par in pares}
    jogos = {par[LADO_JOGO] for par in pares}
    return EtapaFunil(nome, len(usuarios), len(jogos), len(pares))
