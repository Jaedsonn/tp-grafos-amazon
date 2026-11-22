import csv
from collections.abc import Iterable
from typing import TextIO

from src.etl.leitura import CATEGORIA_AUSENTE
from src.comum.tipos import EtapaFunil, Jogo, PesosArestas


def escrever_tabela(
    cabecalho: list[str], linhas: Iterable[list[object]], fluxo: TextIO
) -> None:
    """
    :param cabecalho: nomes das colunas
    :param linhas: valores, na ordem do cabeçalho
    :param fluxo: destino de texto

    Exemplo:
        >>> import io; saida = io.StringIO()
        >>> escrever_tabela(["a"], [[1]], saida); saida.getvalue().split()
        ['a', '1']
    """
    escritor = csv.writer(fluxo, lineterminator="\n")
    escritor.writerow(cabecalho)
    escritor.writerows(linhas)


def formatar_markdown(cabecalho: list[str], linhas: Iterable[list[object]]) -> str:
    """
    :param cabecalho: nomes das colunas
    :param linhas: valores, na ordem do cabeçalho
    :return: tabela Markdown, para exibir no notebook sem depender do pandas

    Exemplo:
        >>> print(formatar_markdown(["a", "b"], [[1, 2]]))
        | a | b |
        |---|---|
        | 1 | 2 |
    """
    topo = "| " + " | ".join(cabecalho) + " |"
    separador = "|" + "---|" * len(cabecalho)
    corpo = ["| " + " | ".join(str(v) for v in linha) + " |" for linha in linhas]
    return "\n".join([topo, separador, *corpo])


def escrever_funil_csv(etapas: list[EtapaFunil], fluxo: TextIO) -> None:
    """
    :param etapas: passos na ordem de aplicação
    :param fluxo: destino de texto

    Exemplo:
        >>> import io; saida = io.StringIO()
        >>> escrever_funil_csv([EtapaFunil("x", None, 3, 2)], saida); saida.getvalue().split()
        ['etapa,usuarios,jogos,arestas', 'x,,3,2']
    """
    linhas = ([e.nome, e.usuarios, e.jogos, e.arestas] for e in etapas)
    escrever_tabela(["etapa", "usuarios", "jogos", "arestas"], linhas, fluxo)


def escrever_arestas_csv(pesos: PesosArestas, fluxo: TextIO) -> None:
    """
    :param pesos: arestas {(p, q): w}
    :param fluxo: destino de texto

    Exemplo:
        >>> import io; saida = io.StringIO()
        >>> escrever_arestas_csv({("1", "2"): 3}, saida); saida.getvalue().split()
        ['Source,Target,Weight', '1,2,3']
    """
    linhas = ([p, q, w] for (p, q), w in sorted(pesos.items()))
    escrever_tabela(["Source", "Target", "Weight"], linhas, fluxo)


def escrever_componentes_csv(tamanhos: dict[int, int], fluxo: TextIO) -> None:
    """
    :param tamanhos: mapa tamanho da componente -> quantidade
    :param fluxo: destino de texto

    Exemplo:
        >>> import io; saida = io.StringIO()
        >>> escrever_componentes_csv({5: 1, 1: 3}, saida); saida.getvalue().split()
        ['tamanho,quantidade', '5,1', '1,3']
    """
    linhas = ([tamanho, quantidade] for tamanho, quantidade in tamanhos.items())
    escrever_tabela(["tamanho", "quantidade"], linhas, fluxo)


def escrever_jogos_csv(
    graus_bipartidos: dict[str, int], catalogo: dict[str, Jogo], fluxo: TextIO
) -> None:
    """
    :param graus_bipartidos: k_p (nº de avaliadores após T2) de cada vértice exportado
    :param catalogo: metadados asin -> Jogo
    :param fluxo: destino de texto

    Exemplo:
        >>> import io; saida = io.StringIO()
        >>> escrever_jogos_csv({"J1": 7}, {}, saida); saida.getvalue().split()
        ['Id,Label,plataforma,tipo,k_p', 'J1,desconhecido,desconhecida,desconhecida,7']
    """
    linhas = []
    for asin, grau in sorted(graus_bipartidos.items()):
        jogo = catalogo.get(
            asin, Jogo(asin, "desconhecido", CATEGORIA_AUSENTE, CATEGORIA_AUSENTE)
        )
        linhas.append([asin, jogo.titulo, jogo.plataforma, jogo.tipo, grau])
    escrever_tabela(["Id", "Label", "plataforma", "tipo", "k_p"], linhas, fluxo)
