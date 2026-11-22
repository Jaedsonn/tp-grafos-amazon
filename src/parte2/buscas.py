from dataclasses import dataclass

from src.comum.grafo import visitar_em_largura
from src.comum.tipos import Adjacencia, ArestaJogos


@dataclass(frozen=True)
class Eulerianidade:
    """Diagnóstico de Euler: circuito exige conexo e 0 ímpares; caminho, conexo e 2 ímpares"""

    conexo: bool
    vertices_grau_impar: int
    tem_circuito: bool
    tem_caminho: bool


@dataclass(frozen=True)
class PontesArticulacoes:
    """Resultado do low-link de Tarjan num grafo não dirigido"""

    pontes: set[ArestaJogos]
    articulacoes: set[str]


def visitar_em_profundidade(adjacencia: Adjacencia, origem: str) -> list[str]:
    """
    :param adjacencia: grafo não dirigido
    :param origem: vértice inicial, presente em adjacencia
    :return: vértices em pré-ordem da DFS

    Exemplo:
        >>> visitar_em_profundidade({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}}, "1")
        ['1', '2', '3']
    """
    if origem not in adjacencia:
        raise KeyError(
            f"origem {origem!r} não está no grafo; esperado um vértice existente"
        )
    visitados: set[str] = set()
    ordem: list[str] = []
    pilha = [origem]
    while pilha:
        atual = pilha.pop()
        if atual in visitados:
            continue
        visitados.add(atual)
        ordem.append(atual)
        pilha.extend(v for v in adjacencia[atual] if v not in visitados)
    return ordem


def diagnosticar_euler(adjacencia: Adjacencia) -> Eulerianidade:
    """
    :param adjacencia: grafo não dirigido, não vazio
    :return: Eulerianidade com conexidade e contagem de vértices de grau ímpar

    Exemplo:
        >>> diagnosticar_euler({"1": {"2", "3"}, "2": {"1", "3"}, "3": {"1", "2"}}).tem_circuito
        True
    """
    if not adjacencia:
        raise ValueError("grafo vazio; esperado ao menos um vértice")
    origem = next(iter(adjacencia))
    conexo = len(visitar_em_largura(adjacencia, origem)) == len(adjacencia)
    impares = sum(1 for vizinhos in adjacencia.values() if len(vizinhos) % 2 == 1)
    return Eulerianidade(
        conexo, impares, conexo and impares == 0, conexo and impares == 2
    )


def encontrar_pontes_e_articulacoes(adjacencia: Adjacencia) -> PontesArticulacoes:
    """
    :param adjacencia: grafo não dirigido e simples
    :return: pontes {(p, q) com p < q} e pontos de articulação, via low-link de Tarjan

    Exemplo:
        >>> r = encontrar_pontes_e_articulacoes({"1": {"2"}, "2": {"1", "3"}, "3": {"2"}})
        >>> sorted(r.pontes), r.articulacoes
        ([('1', '2'), ('2', '3')], {'2'})
    """
    descoberta: dict[str, int] = {}
    menor: dict[str, int] = {}
    pontes: set[ArestaJogos] = set()
    articulacoes: set[str] = set()
    for raiz in adjacencia:
        if raiz not in descoberta:
            explorar_low_link(adjacencia, raiz, descoberta, menor, pontes, articulacoes)
    return PontesArticulacoes(pontes, articulacoes)


def explorar_low_link(
    adjacencia: Adjacencia,
    raiz: str,
    descoberta: dict[str, int],
    menor: dict[str, int],
    pontes: set[ArestaJogos],
    articulacoes: set[str],
) -> None:
    """
    :param adjacencia: grafo não dirigido e simples
    :param raiz: vértice ainda não descoberto onde a DFS começa
    :param descoberta: tempo de descoberta de cada vértice (preenchido aqui)
    :param menor: low-link, o menor tempo alcançável pela subárvore com uma aresta de retorno
    :param pontes: conjunto acumulador de pontes
    :param articulacoes: conjunto acumulador de articulações

    Exemplo:
        explorar_low_link(adjacencia, "B000ABC", {}, {}, set(), set())
    """
    descoberta[raiz] = menor[raiz] = len(descoberta)
    pilha = [(raiz, "", iter(adjacencia[raiz]))]
    filhos_da_raiz = 0
    while pilha:
        v, pai, vizinhos = pilha[-1]
        filho = next(vizinhos, None)
        if filho is None:
            pilha.pop()
            if pai:
                fechar_filho(pai, v, descoberta, menor, pontes, articulacoes, raiz)
            continue
        if filho == pai:
            continue
        if filho in descoberta:
            menor[v] = min(menor[v], descoberta[filho])
            continue
        descoberta[filho] = menor[filho] = len(descoberta)
        filhos_da_raiz += v == raiz
        pilha.append((filho, v, iter(adjacencia[filho])))
    if filhos_da_raiz > 1:
        articulacoes.add(raiz)


def fechar_filho(
    pai: str,
    filho: str,
    descoberta: dict[str, int],
    menor: dict[str, int],
    pontes: set[ArestaJogos],
    articulacoes: set[str],
    raiz: str,
) -> None:
    """
    :param pai: vértice que recebe o low-link do filho
    :param filho: vértice cuja subárvore acabou de ser explorada
    :param descoberta: tempos de descoberta
    :param menor: low-links
    :param pontes: acumulador de pontes
    :param articulacoes: acumulador de articulações
    :param raiz: raiz da DFS atual, tratada à parte pela contagem de filhos

    Exemplo:
        fechar_filho("1", "2", {"1": 0, "2": 1}, {"1": 0, "2": 1}, set(), set(), "1")
    """
    menor[pai] = min(menor[pai], menor[filho])
    if menor[filho] > descoberta[pai]:
        pontes.add((min(pai, filho), max(pai, filho)))
    if pai != raiz and menor[filho] >= descoberta[pai]:
        articulacoes.add(pai)
