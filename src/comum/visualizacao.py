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


CORES_FABRICANTE = {
    "Sony": "#2F6DB5",
    "Microsoft": "#3C9A3C",
    "Nintendo": "#D2423A",
    "Sega": "#7E57C2",
    "Computador": "#8C8C8C",
    "outras": "#C9A227",
}


def desenhar_mapa_de_familias(
    ligacoes: dict[tuple[str, str], float],
    produtos: dict[str, int],
    fabricantes: dict[str, str],
) -> Figure:
    """
    :param ligacoes: {(família, família): razão observado/esperado}
    :param produtos: produtos de cada família, que define o tamanho do nó
    :param fabricantes: fabricante de cada família, que define a cor
    :return: grafo reduzido entre famílias; a espessura e a cor da aresta crescem com a razão

    Exemplo:
        figura = desenhar_mapa_de_familias({("Wii", "Wii U"): 3.2}, {"Wii": 1393, "Wii U": 331}, {"Wii": "Nintendo", "Wii U": "Nintendo"})
    """
    grafo = nx.Graph()
    grafo.add_nodes_from(produtos)
    grafo.add_weighted_edges_from((a, b, r) for (a, b), r in ligacoes.items())
    posicoes = nx.kamada_kawai_layout(grafo, weight=None)
    figura, eixo = plt.subplots(figsize=(8, 7))
    for a, b, razao in grafo.edges(data="weight"):
        intensidade = min(1.0, np.log2(razao) / np.log2(25))
        eixo.plot(
            *zip(posicoes[a], posicoes[b]),
            color=plt.get_cmap("Greys")(0.35 + 0.6 * intensidade),
            lw=0.6 + 3.5 * intensidade,
            zorder=1,
        )
    for familia, quantidade in produtos.items():
        x, y = posicoes[familia]
        eixo.scatter(
            x,
            y,
            s=30 + quantidade / 4,
            color=CORES_FABRICANTE[fabricantes[familia]],
            edgecolor="white",
            zorder=2,
        )
        eixo.text(x, y - 0.06, familia, ha="center", va="top", fontsize=7, zorder=3)
    for fabricante in dict.fromkeys(fabricantes.values()):
        eixo.scatter([], [], color=CORES_FABRICANTE[fabricante], label=fabricante)
    eixo.legend(frameon=False, fontsize=8, loc="lower left")
    eixo.set_axis_off()
    figura.tight_layout()
    return figura


def desenhar_panelas(
    pesos: PesosArestas, familias: dict[str, str], forca: dict[str, int], semente: int
) -> Figure:
    """
    :param pesos: arestas do subgrafo reduzido
    :param familias: família de cada vértice; define a cor e o rótulo de cada grupo
    :param forca: força de cada vértice no grafo completo, que define o tamanho do nó
    :param semente: SEED do layout por forças
    :return: arestas dentro da família na cor dela, entre famílias em cinza, e o nome de cada
        família na mediana das posições dos seus produtos

    Exemplo:
        figura = desenhar_panelas(pesos_reduzidos, familias, forca, config.SEED)
    """
    grafo = nx.Graph()
    grafo.add_weighted_edges_from((p, q, w) for (p, q), w in pesos.items())
    posicoes = nx.spring_layout(grafo, weight="weight", seed=semente, iterations=300)
    presentes = sorted(
        {familias[v] for v in grafo},
        key=lambda f: -sum(familias[v] == f for v in grafo),
    )
    escuras = [c for i, c in enumerate(plt.get_cmap("tab10").colors) if i != 7]
    claras = [
        c for i, c in enumerate(plt.get_cmap("tab20").colors) if i % 2 and i != 15
    ]
    paleta = escuras + claras
    cor = {f: paleta[i % len(paleta)] for i, f in enumerate(presentes)}
    figura, eixo = plt.subplots(figsize=(9, 9))
    for p, q in grafo.edges():
        mesma = familias[p] == familias[q]
        eixo.plot(
            *zip(posicoes[p], posicoes[q]),
            color=cor[familias[p]] if mesma else "#BBBBBB",
            alpha=0.6 if mesma else 0.35,
            lw=0.8 if mesma else 0.4,
            zorder=1,
        )
    for familia in presentes:
        vertices = [v for v in grafo if familias[v] == familia]
        xy = np.array([posicoes[v] for v in vertices])
        eixo.scatter(
            xy[:, 0],
            xy[:, 1],
            s=[8 + forca[v] / 60 for v in vertices],
            color=cor[familia],
            edgecolor="white",
            linewidth=0.3,
            zorder=2,
        )
        cx, cy = np.median(xy, axis=0)
        eixo.text(
            cx,
            cy,
            familia,
            fontsize=8,
            weight="bold",
            ha="center",
            zorder=3,
            bbox={"fc": "white", "ec": "none", "alpha": 0.7, "pad": 1},
        )
    eixo.set_axis_off()
    figura.tight_layout()
    return figura
