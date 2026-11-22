"""
Papel dos consoles na rede de coavaliação.

Os metadados da categoria guardam dois níveis de rótulo: ``plataforma`` (category[1]) e
``tipo`` (category[2]). Eles não são homogêneos: em "Retro Gaming & Microconsoles" e em
"Kids & Family" o console aparece no ``tipo``, e não na ``plataforma``. Este módulo
normaliza os dois níveis em uma **classe de produto** (console, acessório, jogo, ...) e
em uma **família de console** (Wii, PlayStation 4, PC, ...), e mede como as arestas se
concentram entre elas.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass

import numpy as np

from src.comum.tipos import Adjacencia, Jogo, PesosArestas

CONSOLE = "console"
ACESSORIO = "acessório"
JOGO = "jogo"
RETRO = "retrô"
OUTROS = "outros"
SEM_ROTULO = "sem rótulo"
CLASSES = (CONSOLE, ACESSORIO, JOGO, RETRO, OUTROS, SEM_ROTULO)

DESCONHECIDA = "desconhecida"
_TIPOS_JOGO = {"Games", "Digital Games & DLC"}
_TIPOS_OUTROS = {
    "Interactive Gaming Figures",
    "Currency & Subscription Cards",
    "Currency Cards",
    "Points Cards",
    "Virtual Reality",
}
_PLATAFORMAS_COM_CONSOLE_NO_TIPO = {
    "Retro Gaming & Microconsoles",
    "Kids & Family",
    "Digital Games",
}
_NOMES_FAMILIA = {"Nintendo 3DS & 2DS": "Nintendo 3DS"}


def rotulo_valido(texto: str) -> bool:
    """
    :param texto: valor de plataforma ou tipo vindo dos metadados
    :return: False para ausência ou para restos de HTML do scraping

    Exemplo:
        >>> rotulo_valido("Wii"), rotulo_valido("</span></span>"), rotulo_valido("desconhecida")
        (True, False, False)
    """
    return bool(texto) and texto != DESCONHECIDA and "<" not in texto


def classificar_produto(jogo: Jogo) -> str:
    """
    :param jogo: produto com plataforma e tipo
    :return: uma das CLASSES

    Exemplo:
        >>> classificar_produto(Jogo("a", "PS4 Pro", "PlayStation 4", "Consoles"))
        'console'
        >>> classificar_produto(Jogo("b", "Controle", "Xbox 360", "Accessories"))
        'acessório'
        >>> classificar_produto(Jogo("c", "Zelda", "Retro Gaming & Microconsoles", "Nintendo 64"))
        'retrô'
        >>> classificar_produto(Jogo("d", "?", "PC", "</span>"))
        'sem rótulo'
    """
    plataforma, tipo = jogo.plataforma, jogo.tipo
    if tipo == "Consoles":
        return CONSOLE
    if tipo == "Accessories" or plataforma == "Accessories":
        return ACESSORIO
    if tipo in _TIPOS_JOGO:
        return JOGO
    if tipo in _TIPOS_OUTROS:
        return OUTROS
    if plataforma == "Retro Gaming & Microconsoles" and rotulo_valido(tipo):
        return RETRO
    if plataforma in _PLATAFORMAS_COM_CONSOLE_NO_TIPO and rotulo_valido(tipo):
        return JOGO
    return SEM_ROTULO


def familia_de_console(jogo: Jogo) -> str:
    """
    :param jogo: produto com plataforma e tipo
    :return: console a que o produto pertence, com o mesmo nome nos dois níveis de rótulo

    Exemplo:
        >>> familia_de_console(Jogo("a", "x", "Kids & Family", "Nintendo 3DS"))
        'Nintendo 3DS'
        >>> familia_de_console(Jogo("b", "x", "Nintendo 3DS & 2DS", "Games"))
        'Nintendo 3DS'
        >>> familia_de_console(Jogo("c", "x", "Accessories", "desconhecida"))
        'desconhecida'
    """
    if jogo.plataforma in _PLATAFORMAS_COM_CONSOLE_NO_TIPO:
        bruto = jogo.tipo
    elif jogo.plataforma == "Accessories":
        bruto = DESCONHECIDA
    else:
        bruto = jogo.plataforma
    if not rotulo_valido(bruto):
        return DESCONHECIDA
    return _NOMES_FAMILIA.get(bruto, bruto)


@dataclass(frozen=True)
class Participacao:
    """Quanto de vértices, pontas de aresta e força uma classe concentra"""

    classe: str
    vertices: int
    fracao_vertices: float
    fracao_pontas: float
    fracao_forca: float
    grau_medio: float


def medir_participacao(
    pesos: PesosArestas, rotulos: dict[str, str]
) -> list[Participacao]:
    """
    :param pesos: arestas {(p, q): w}
    :param rotulos: classe de cada vértice
    :return: uma Participacao por classe, na ordem de mais vértices para menos

    Exemplo:
        >>> pesos = {("c", "j1"): 3, ("c", "j2"): 1, ("j1", "j2"): 1}
        >>> p = medir_participacao(pesos, {"c": "console", "j1": "jogo", "j2": "jogo"})
        >>> [(x.classe, x.vertices, round(x.fracao_pontas, 2), x.fracao_forca) for x in p]
        [('jogo', 2, 0.67, 0.6), ('console', 1, 0.33, 0.4)]
    """
    vertices = Counter(rotulos.values())
    pontas: Counter[str] = Counter()
    forca: Counter[str] = Counter()
    for (p, q), w in pesos.items():
        for v in (p, q):
            pontas[rotulos[v]] += 1
            forca[rotulos[v]] += w
    total_v, total_p, total_f = len(rotulos), sum(pontas.values()), sum(forca.values())
    return [
        Participacao(
            classe,
            quantidade,
            quantidade / total_v,
            pontas[classe] / total_p,
            forca[classe] / total_f,
            pontas[classe] / quantidade,
        )
        for classe, quantidade in vertices.most_common()
    ]


def calcular_mistura(
    pesos: PesosArestas, rotulos: dict[str, str], ponderada: bool = False
) -> tuple[dict[tuple[str, str], float], dict[str, float]]:
    """
    Matriz de mistura de Newman (2003): e_ab é a fração das pontas de aresta que ligam
    a a b, contada nos dois sentidos, e a_a = Σ_b e_ab.

    :param pesos: arestas {(p, q): w}
    :param rotulos: rótulo de cada vértice
    :param ponderada: se True, cada aresta conta w vezes
    :return: (e, a)

    Exemplo:
        >>> e, a = calcular_mistura({("x", "y"): 1, ("y", "z"): 1}, {"x": "A", "y": "A", "z": "B"})
        >>> e[("A", "A")], e[("A", "B")], a["A"]
        (0.5, 0.25, 0.75)
    """
    e: dict[tuple[str, str], float] = defaultdict(float)
    total = 0.0
    for (p, q), w in pesos.items():
        peso = w if ponderada else 1
        rp, rq = rotulos[p], rotulos[q]
        e[(rp, rq)] += peso
        e[(rq, rp)] += peso
        total += 2 * peso
    e = {par: valor / total for par, valor in e.items()}
    a: dict[str, float] = defaultdict(float)
    for (ra, _), valor in e.items():
        a[ra] += valor
    return e, dict(a)


def calcular_assortatividade(
    pesos: PesosArestas, rotulos: dict[str, str], ponderada: bool = False
) -> float:
    """
    Coeficiente de assortatividade categórica, r = (Σ e_aa − Σ a_a²) / (1 − Σ a_a²).
    r = 1: só há arestas dentro do mesmo rótulo; r = 0: mistura ao acaso; r < 0: os
    rótulos se evitam.

    :param pesos: arestas {(p, q): w}
    :param rotulos: rótulo de cada vértice
    :param ponderada: se True, cada aresta conta w vezes
    :return: r

    Exemplo:
        >>> calcular_assortatividade({("a", "b"): 1, ("c", "d"): 1}, {"a": 1, "b": 1, "c": 2, "d": 2})
        1.0
        >>> calcular_assortatividade({("a", "c"): 1, ("b", "d"): 1}, {"a": 1, "b": 1, "c": 2, "d": 2})
        -1.0
    """
    e, a = calcular_mistura(pesos, rotulos, ponderada)
    dentro = sum(e.get((r, r), 0.0) for r in a)
    acaso = sum(valor**2 for valor in a.values())
    return (dentro - acaso) / (1 - acaso)


@dataclass(frozen=True)
class PermutacaoHomofilia:
    """Fração de arestas dentro do mesmo rótulo, real e sob rótulos embaralhados"""

    observada: float
    media_nula: float
    dp_nulo: float
    maior_nula: float
    permutacoes: int


def permutar_rotulos_homofilia(
    pesos: PesosArestas, rotulos: dict[str, str], permutacoes: int, semente: int
) -> PermutacaoHomofilia:
    """
    Embaralha os rótulos entre os vértices, preservando quantos vértices há de cada rótulo e
    a topologia, e recalcula a fração de arestas com as duas pontas no mesmo rótulo.

    :param pesos: arestas {(p, q): w}
    :param rotulos: rótulo de cada vértice
    :param permutacoes: quantas permutações sortear
    :param semente: semente do sorteio
    :return: PermutacaoHomofilia

    Exemplo:
        >>> pesos = {("a", "b"): 1, ("c", "d"): 1, ("e", "f"): 1}
        >>> t = permutar_rotulos_homofilia(pesos, dict(zip("abcdef", "XXYYZZ")), 200, 1)
        >>> t.observada, t.maior_nula <= 1.0, t.media_nula < 0.5
        (1.0, True, True)
    """
    vertices = sorted(rotulos)
    indice = {v: i for i, v in enumerate(vertices)}
    codigos = {r: i for i, r in enumerate(sorted(set(rotulos.values()), key=str))}
    rotulo = np.array([codigos[rotulos[v]] for v in vertices])
    origem = np.array([indice[p] for p, _ in pesos])
    destino = np.array([indice[q] for _, q in pesos])
    observada = float(np.mean(rotulo[origem] == rotulo[destino]))
    gerador = np.random.default_rng(semente)
    nulos = np.empty(permutacoes)
    for i in range(permutacoes):
        embaralhado = gerador.permutation(rotulo)
        nulos[i] = np.mean(embaralhado[origem] == embaralhado[destino])
    return PermutacaoHomofilia(
        observada,
        float(nulos.mean()),
        float(nulos.std(ddof=1)),
        float(nulos.max()),
        permutacoes,
    )


def calcular_gini(valores: list[float]) -> float:
    """
    :param valores: quantidades não negativas
    :return: índice de Gini, 0 = todos iguais, perto de 1 = tudo em um só

    Exemplo:
        >>> calcular_gini([1, 1, 1, 1])
        0.0
        >>> calcular_gini([0, 0, 0, 4])
        0.75
    """
    ordenados = np.sort(np.asarray(valores, dtype=float))
    n = len(ordenados)
    acumulado = np.cumsum(ordenados)
    return float((n + 1 - 2 * np.sum(acumulado) / acumulado[-1]) / n)


@dataclass(frozen=True)
class CoberturaConsole:
    """Quanto do catálogo de uma família está a uma aresta de um console da família"""

    familia: str
    produtos: int
    consoles: int
    cobertos: int
    fracao_coberta: float


def medir_cobertura_dos_consoles(
    adjacencia: Adjacencia, classes: dict[str, str], familias: dict[str, str]
) -> list[CoberturaConsole]:
    """
    :param adjacencia: vizinhos de cada vértice
    :param classes: classe de cada vértice
    :param familias: família de console de cada vértice
    :return: uma linha por família que tem ao menos um console, da mais coberta para a menos

    Exemplo:
        >>> adj = {"c": {"j1"}, "j1": {"c", "j2"}, "j2": {"j1"}}
        >>> cl = {"c": "console", "j1": "jogo", "j2": "jogo"}
        >>> medir_cobertura_dos_consoles(adj, cl, {"c": "Wii", "j1": "Wii", "j2": "Wii"})
        [CoberturaConsole(familia='Wii', produtos=2, consoles=1, cobertos=1, fracao_coberta=0.5)]
    """
    consoles = defaultdict(set)
    produtos = defaultdict(set)
    for v, familia in familias.items():
        (consoles if classes[v] == CONSOLE else produtos)[familia].add(v)
    linhas = []
    for familia, grupo in consoles.items():
        alvo = produtos[familia]
        if not alvo:
            continue
        vizinhos = set().union(*(adjacencia[c] for c in grupo))
        cobertos = len(alvo & vizinhos)
        linhas.append(
            CoberturaConsole(
                familia, len(alvo), len(grupo), cobertos, cobertos / len(alvo)
            )
        )
    return sorted(linhas, key=lambda c: c.fracao_coberta, reverse=True)


def contar_arestas_entre_consoles(
    pesos: PesosArestas, classes: dict[str, str], familias: dict[str, str]
) -> Counter[tuple[str, str]]:
    """
    :param pesos: arestas {(p, q): w}
    :param classes: classe de cada vértice
    :param familias: família de console de cada vértice
    :return: soma dos pesos das arestas console–console, por par de famílias em ordem alfabética

    Exemplo:
        >>> pesos = {("a", "b"): 4, ("a", "c"): 2}
        >>> cl = {"a": "console", "b": "console", "c": "jogo"}
        >>> contar_arestas_entre_consoles(pesos, cl, {"a": "Xbox One", "b": "PlayStation 4", "c": "PC"})
        Counter({('PlayStation 4', 'Xbox One'): 4})
    """
    contagem: Counter[tuple[str, str]] = Counter()
    for (p, q), w in pesos.items():
        if classes[p] == CONSOLE and classes[q] == CONSOLE:
            contagem[tuple(sorted((familias[p], familias[q])))] += w
    return contagem
