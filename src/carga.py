import csv
import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from src.grafo import montar_adjacencia
from src.tipos import Adjacencia, Jogo, PesosArestas


@dataclass(frozen=True)
class GrafoAnalise:
    """LCC pronta para as Partes I–III, com rótulos para interpretar os vértices"""

    adjacencia: Adjacencia
    pesos: PesosArestas
    jogos: dict[str, Jogo]
    graus_bipartidos: dict[str, int]


def ler_arestas_ponderadas(fluxo: TextIO) -> PesosArestas:
    """
    :param fluxo: CSV com cabeçalho Source,Target,Weight
    :return: arestas {(p, q): w}

    Exemplo:
        >>> import io
        >>> ler_arestas_ponderadas(io.StringIO("Source,Target,Weight\\n1,2,3\\n"))
        {('1', '2'): 3}
    """
    return {
        (linha["Source"], linha["Target"]): int(linha["Weight"])
        for linha in csv.DictReader(fluxo)
    }


def ler_jogos_rotulados(fluxo: TextIO) -> tuple[dict[str, Jogo], dict[str, int]]:
    """
    :param fluxo: CSV com cabeçalho Id,Label,plataforma,tipo,k_p
    :return: catálogo asin -> Jogo e k_p de cada vértice

    Exemplo:
        >>> import io
        >>> jogos, graus = ler_jogos_rotulados(io.StringIO("Id,Label,plataforma,tipo,k_p\\nJ1,Halo,Xbox 360,Games,9\\n"))
        >>> jogos["J1"].titulo, graus["J1"]
        ('Halo', 9)
    """
    jogos: dict[str, Jogo] = {}
    graus: dict[str, int] = {}
    for linha in csv.DictReader(fluxo):
        asin = linha["Id"]
        jogos[asin] = Jogo(asin, linha["Label"], linha["plataforma"], linha["tipo"])
        graus[asin] = int(linha["k_p"])
    return jogos, graus


def ler_tamanhos_componentes(fluxo: TextIO) -> dict[int, int]:
    """
    :param fluxo: CSV com cabeçalho tamanho,quantidade
    :return: mapa tamanho da componente -> quantidade

    Exemplo:
        >>> import io
        >>> ler_tamanhos_componentes(io.StringIO("tamanho,quantidade\\n5,1\\n1,3\\n"))
        {5: 1, 1: 3}
    """
    return {
        int(linha["tamanho"]): int(linha["quantidade"])
        for linha in csv.DictReader(fluxo)
    }


def carregar_grafo_analise(dir_processado: Path) -> GrafoAnalise:
    """
    :param dir_processado: pasta com arestas_lcc.csv.gz e jogos_lcc.csv gerados pelo ETL
    :return: GrafoAnalise da LCC

    Exemplo:
        grafo = carregar_grafo_analise(config.DIR_PROCESSADO)
    """
    with gzip.open(
        dir_processado / "arestas_lcc.csv.gz", "rt", encoding="utf-8"
    ) as fluxo:
        pesos = ler_arestas_ponderadas(fluxo)
    with open(dir_processado / "jogos_lcc.csv", encoding="utf-8", newline="") as fluxo:
        jogos, graus_bipartidos = ler_jogos_rotulados(fluxo)
    return GrafoAnalise(montar_adjacencia(pesos), pesos, jogos, graus_bipartidos)
