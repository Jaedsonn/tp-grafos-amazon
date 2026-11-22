import csv
import html
import json
from typing import TextIO

from src.tipos import Jogo, ParAvaliacao

CATEGORIA_AUSENTE: str = "desconhecida"


def ler_pares_avaliacao(fluxo: TextIO) -> list[ParAvaliacao]:
    """
    :param fluxo: texto CSV sem cabeçalho no formato item,user,rating,timestamp
    :return: lista de pares (usuário, jogo), com repetições (a dedup é o passo T1)

    Exemplo:
        >>> import io
        >>> ler_pares_avaliacao(io.StringIO("J1,U1,5.0,1\\n"))
        [('U1', 'J1')]
    """
    pares: list[ParAvaliacao] = []
    for numero, linha in enumerate(csv.reader(fluxo), start=1):
        if len(linha) != 4:
            raise ValueError(
                f"linha {numero} inválida: {linha!r}; esperado item,user,rating,timestamp"
            )
        pares.append((linha[1], linha[0]))
    return pares


def ler_catalogo_jogos(fluxo: TextIO) -> dict[str, Jogo]:
    """
    :param fluxo: texto com um objeto JSON por linha, cada um com a chave "asin"
    :return: catálogo; em asin repetido, a primeira ocorrência vence

    Exemplo:
        >>> import io
        >>> linha = '{"asin": "J1", "title": "Halo", "category": ["Video Games", "Xbox 360", "Games"]}'
        >>> ler_catalogo_jogos(io.StringIO(linha))["J1"].plataforma
        'Xbox 360'
    """
    catalogo: dict[str, Jogo] = {}
    for linha in fluxo:
        jogo = extrair_jogo(json.loads(linha))
        catalogo.setdefault(jogo.asin, jogo)
    return catalogo


def extrair_jogo(registro: dict[str, object]) -> Jogo:
    """
    :param registro: objeto JSON decodificado de uma linha dos metadados
    :return: Jogo com plataforma = category[1] e tipo = category[2]

    Exemplo:
        >>> extrair_jogo({"asin": "J1", "title": "A &amp; B"}).titulo
        'A & B'
    """
    if "asin" not in registro:
        raise ValueError(
            f"registro sem 'asin': {registro!r}; esperado objeto com chave asin"
        )
    categorias = registro.get("category")
    categorias = categorias if isinstance(categorias, list) else []
    return Jogo(
        asin=str(registro["asin"]),
        titulo=html.unescape(str(registro.get("title", ""))).strip(),
        plataforma=ler_categoria(categorias, 1),
        tipo=ler_categoria(categorias, 2),
    )


def ler_categoria(categorias: list[object], nivel: int) -> str:
    """
    :param categorias: lista hierárquica, ex.: ["Video Games", "Wii", "Games"]
    :param nivel: índice na hierarquia (1 = plataforma, 2 = tipo)
    :return: rótulo limpo de entidades HTML

    Exemplo:
        >>> ler_categoria(["Video Games", "Retro Gaming &amp; Microconsoles"], 1)
        'Retro Gaming & Microconsoles'
    """
    if len(categorias) <= nivel:
        return CATEGORIA_AUSENTE
    return html.unescape(str(categorias[nivel])).strip()
