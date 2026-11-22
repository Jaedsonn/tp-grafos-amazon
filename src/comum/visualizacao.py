from collections import Counter
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.figure import Figure

from src.comum.tipos import Jogo, PesosArestas

MAX_PLATAFORMAS_NA_LEGENDA: int = 8
COR_OUTRAS: str = "#B4B2A9"


def salvar_figura(figura: Figure, destino: Path) -> None:
    """
    :param figura: figura do matplotlib
    :param destino: caminho sem extensão; grava .pdf (relatório) e .png (README e notebook)

    Exemplo:
        salvar_figura(figura, config.RAIZ / "imagens" / "parte1_graus")
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    for extensao in ("pdf", "png"):
        figura.savefig(
            destino.with_suffix(f".{extensao}"), dpi=200, bbox_inches="tight"
        )


def plotar_distribuicao_graus(
    distribuicao: dict[int, int], ccdf: dict[int, float]
) -> Figure:
    """
    :param distribuicao: histograma k -> quantidade
    :param ccdf: P(K >= k) por k
    :return: figura com P(k) e CCDF lado a lado, ambos em log-log

    Exemplo:
        figura = plotar_distribuicao_graus({1: 3, 2: 1}, {1: 1.0, 2: 0.25})
    """
    total = sum(distribuicao.values())
    figura, (eixo_pk, eixo_ccdf) = plt.subplots(1, 2, figsize=(10, 4))
    eixo_pk.loglog(
        list(distribuicao), [q / total for q in distribuicao.values()], "o", ms=3
    )
    eixo_pk.set(xlabel="grau k", ylabel="P(k)", title="Distribuição de graus")
    eixo_ccdf.loglog(list(ccdf), list(ccdf.values()), "-", lw=1.5)
    eixo_ccdf.set(xlabel="grau k", ylabel="P(K ≥ k)", title="CCDF")
    for eixo in (eixo_pk, eixo_ccdf):
        eixo.grid(True, which="major", alpha=0.3)
    figura.tight_layout()
    return figura


def colorir_por_plataforma(
    vertices: list[str], jogos: dict[str, Jogo]
) -> tuple[list[str], dict[str, str]]:
    """
    :param vertices: vértices na ordem do desenho
    :param jogos: catálogo com a plataforma de cada vértice
    :return: cor de cada vértice e legenda plataforma -> cor (as demais ficam cinza)

    Exemplo:
        >>> cores, legenda = colorir_por_plataforma(["a"], {"a": Jogo("a", "t", "Wii", "Games")})
        >>> list(legenda)
        ['Wii']
    """
    frequencia = Counter(jogos[v].plataforma for v in vertices)
    principais = [p for p, _ in frequencia.most_common(MAX_PLATAFORMAS_NA_LEGENDA)]
    paleta = plt.get_cmap("tab10").colors
    legenda = {p: matplotlib.colors.to_hex(paleta[i]) for i, p in enumerate(principais)}
    return [legenda.get(jogos[v].plataforma, COR_OUTRAS) for v in vertices], legenda


def desenhar_subgrafo(
    pesos: PesosArestas, jogos: dict[str, Jogo], graus: dict[str, int], semente: int
) -> Figure:
    """
    :param pesos: arestas do subgrafo a desenhar
    :param jogos: catálogo para cor (plataforma) e rótulos (título)
    :param graus: grau de cada vértice no grafo completo, que define o tamanho do nó
    :param semente: SEED do layout por forças, para a figura ser reprodutível
    :return: figura com cor por plataforma, tamanho por grau e os 10 maiores hubs rotulados

    Exemplo:
        figura = desenhar_subgrafo(pesos_nucleo, grafo.jogos, graus, config.SEED)
    """
    grafo = nx.Graph()
    grafo.add_weighted_edges_from((p, q, w) for (p, q), w in pesos.items())
    vertices = list(grafo.nodes)
    posicoes = nx.spring_layout(grafo, weight="weight", seed=semente)
    cores, legenda = colorir_por_plataforma(vertices, jogos)
    figura, eixo = plt.subplots(figsize=(10, 10))
    nx.draw_networkx_edges(grafo, posicoes, ax=eixo, alpha=0.05, width=0.5)
    tamanhos = [graus[v] / 8 for v in vertices]
    nx.draw_networkx_nodes(
        grafo, posicoes, ax=eixo, node_color=cores, node_size=tamanhos
    )
    hubs = sorted(vertices, key=graus.__getitem__, reverse=True)[:10]
    rotulos = {v: jogos[v].titulo[:28] for v in hubs}
    nx.draw_networkx_labels(grafo, posicoes, labels=rotulos, ax=eixo, font_size=7)
    for plataforma, cor in legenda.items():
        eixo.scatter([], [], c=cor, label=plataforma)
    eixo.legend(loc="lower left", fontsize=8, frameon=False)
    eixo.set_axis_off()
    return figura


def plotar_escalabilidade(
    series: dict[str, list[tuple[float, float, float]]], rotulo_custo: str
) -> Figure:
    """
    :param series: algoritmo -> pontos (custo teórico, tempo médio, meia largura do IC)
    :param rotulo_custo: texto do eixo x, ex.: "n + m"
    :return: figura log-log do tempo contra o custo; uma reta de inclinação 1 confirma a complexidade

    Exemplo:
        figura = plotar_escalabilidade({"BFS": [(1e3, 1e-3, 1e-5)]}, "n + m")
    """
    figura, eixo = plt.subplots(figsize=(6, 4))
    for algoritmo, pontos in series.items():
        custos, medias, margens = zip(*pontos)
        eixo.errorbar(
            custos, medias, yerr=margens, marker="o", ms=3, capsize=2, label=algoritmo
        )
    eixo.set(xscale="log", yscale="log", xlabel=rotulo_custo, ylabel="tempo médio (s)")
    eixo.grid(True, which="major", alpha=0.3)
    eixo.legend(fontsize=8, frameon=False)
    figura.tight_layout()
    return figura


def plotar_ccdf_com_ajuste(
    ccdf: dict[int, float], gama: float, k_min: int, cauda: float
) -> Figure:
    """
    :param ccdf: P(K >= k) por k
    :param gama: expoente ajustado
    :param k_min: início da cauda
    :param cauda: P(K >= k_min), para a reta começar sobre a curva empírica
    :return: CCDF em log-log com a reta k^(1−γ) da lei de potência na cauda

    Exemplo:
        figura = plotar_ccdf_com_ajuste({1: 1.0, 2: 0.25}, 2.5, 1, 1.0)
    """
    figura, eixo = plt.subplots(figsize=(6, 4))
    eixo.loglog(list(ccdf), list(ccdf.values()), "o", ms=2, label="empírica")
    graus = [k for k in ccdf if k >= k_min]
    modelo = [cauda * ((k - 0.5) / (k_min - 0.5)) ** (1 - gama) for k in graus]
    eixo.loglog(graus, modelo, "-", lw=2, label=f"lei de potência, γ = {gama:.2f}")
    eixo.axvline(k_min, ls=":", color="gray", label=f"k_min = {k_min}")
    eixo.set(xlabel="grau k", ylabel="P(K ≥ k)")
    eixo.grid(True, which="major", alpha=0.3)
    eixo.legend(fontsize=8, frameon=False)
    figura.tight_layout()
    return figura


def plotar_robustez(
    aleatorio: dict[str, list[float]], ataques: dict[str, dict[str, float]]
) -> Figure:
    """
    :param aleatorio: métrica -> valores das T repetições de remoção aleatória
    :param ataques: centralidade -> {métrica: valor após remover o top r}
    :return: um boxplot por métrica (aleatório, com média ± DP) e um marcador por ataque

    Exemplo:
        figura = plotar_robustez({"S": [0.9, 0.95]}, {"grau": {"S": 0.5}})
    """
    figura, eixos = plt.subplots(1, len(aleatorio), figsize=(3 * len(aleatorio), 3.5))
    for eixo, (metrica, valores) in zip(eixos, aleatorio.items()):
        eixo.boxplot(valores, widths=0.5, showmeans=True)
        media, desvio = float(np.mean(valores)), float(np.std(valores, ddof=1))
        eixo.errorbar(1.35, media, yerr=desvio, fmt="o", color="black", capsize=3)
        for posicao, (nome, valores_ataque) in enumerate(ataques.items(), start=2):
            eixo.plot(
                posicao, valores_ataque[metrica], "X", ms=9, label=f"ataque: {nome}"
            )
        eixo.set_xticks(range(1, len(ataques) + 2), ["aleatória", *ataques], fontsize=8)
        eixo.set_title(metrica, fontsize=10)
        eixo.grid(True, axis="y", alpha=0.3)
    figura.tight_layout()
    return figura


def plotar_curvas_de_ataque(
    fracoes: list[float], curvas: dict[str, list[float]]
) -> Figure:
    """
    :param fracoes: frações f de vértices removidos
    :param curvas: estratégia -> S(f)
    :return: S(f) de cada estratégia; a linha vertical marca os 5% do Apêndice C

    Exemplo:
        figura = plotar_curvas_de_ataque([0.0, 0.1], {"grau": [1.0, 0.4]})
    """
    figura, eixo = plt.subplots(figsize=(6, 4))
    for estrategia, curva in curvas.items():
        eixo.plot(fracoes, curva, "o-", ms=3, label=estrategia)
    eixo.axvline(0.05, ls=":", color="gray")
    eixo.set(xlabel="fração removida f", ylabel="S(f)", ylim=(0, 1.02))
    eixo.grid(True, alpha=0.3)
    eixo.legend(fontsize=8, frameon=False)
    figura.tight_layout()
    return figura


def plotar_concentracao_por_classe(
    participacao: dict[str, tuple[float, float]],
    razoes: dict[tuple[str, str], float],
    classes: list[str],
) -> Figure:
    """
    :param participacao: classe -> (fração dos vértices, fração das pontas de aresta)
    :param razoes: (classe a, classe b) -> e_ab / (a_a a_b), observado sobre o esperado
    :param classes: ordem das classes nos dois painéis
    :return: barras de participação (esquerda) e mapa de calor da mistura em escala log (direita)

    Exemplo:
        figura = plotar_concentracao_por_classe({"jogo": (0.5, 0.6)}, {("jogo", "jogo"): 1.3}, ["jogo"])
    """
    figura, (barras, calor) = plt.subplots(1, 2, figsize=(10, 4))
    posicoes = np.arange(len(classes))
    vertices = [participacao[c][0] for c in classes]
    pontas = [participacao[c][1] for c in classes]
    barras.bar(posicoes - 0.2, vertices, 0.4, label="vértices", color=COR_OUTRAS)
    barras.bar(posicoes + 0.2, pontas, 0.4, label="pontas de aresta", color="#2F6DB5")
    barras.set_xticks(posicoes, classes, rotation=30, ha="right", fontsize=8)
    barras.set(ylabel="fração da LCC")
    barras.grid(True, axis="y", alpha=0.3)
    barras.legend(fontsize=8, frameon=False)
    matriz = np.array([[razoes.get((a, b), np.nan) for b in classes] for a in classes])
    imagem = calor.imshow(
        np.log2(matriz), cmap="RdBu_r", vmin=-3, vmax=3, interpolation="nearest"
    )
    for i in range(len(classes)):
        for j in range(len(classes)):
            escuro = abs(np.log2(matriz[i, j])) > 2
            calor.text(
                j,
                i,
                f"{matriz[i, j]:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color="white" if escuro else "black",
            )
    calor.set_xticks(posicoes, classes, rotation=30, ha="right", fontsize=8)
    calor.set_yticks(posicoes, classes, fontsize=8)
    barra_cor = figura.colorbar(imagem, ax=calor, fraction=0.046)
    barra_cor.set_label("log₂(observado / esperado)", fontsize=8)
    figura.tight_layout()
    return figura


def plotar_ccdf_modelos(curvas: dict[str, dict[int, float]]) -> Figure:
    """
    :param curvas: nome do grafo -> CCDF dos graus, P(K >= k) por k
    :return: as CCDFs sobrepostas em log-log; a primeira curva é o grafo real, em preto

    Exemplo:
        figura = plotar_ccdf_modelos({"real": {1: 1.0, 2: 0.3}, "ER": {1: 1.0, 2: 0.9}})
    """
    figura, eixo = plt.subplots(figsize=(6, 4))
    for i, (nome, ccdf) in enumerate(curvas.items()):
        estilo = {"color": "black", "lw": 2} if i == 0 else {"lw": 1.3}
        eixo.loglog(list(ccdf), list(ccdf.values()), "-", label=nome, **estilo)
    eixo.set(xlabel="grau k", ylabel="P(K ≥ k)")
    eixo.grid(True, which="major", alpha=0.3)
    eixo.legend(fontsize=8, frameon=False)
    figura.tight_layout()
    return figura
