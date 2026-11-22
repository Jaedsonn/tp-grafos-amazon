"""Testes de integração da Parte II contra o NetworkX, em grafos aleatórios."""

import random

import networkx as nx
import pytest

from src.parte2.buscas import (
    encontrar_componentes_fortes,
    encontrar_pontes_e_articulacoes,
    orientar_nos_dois_sentidos,
)


def sortear_digrafo(n: int, p: float, semente: int) -> dict[str, set[str]]:
    sorteio = random.Random(semente)
    return {
        str(v): {str(w) for w in range(n) if w != v and sorteio.random() < p}
        for v in range(n)
    }


@pytest.mark.parametrize("semente", range(20))
def test_componentes_fortes_iguais_ao_networkx(semente):
    sucessores = sortear_digrafo(60, 0.03, semente)
    digrafo = nx.DiGraph([(v, w) for v, ws in sucessores.items() for w in ws])
    digrafo.add_nodes_from(sucessores)
    esperado = sorted(
        map(frozenset, nx.strongly_connected_components(digrafo)), key=sorted
    )
    obtido = sorted(
        map(frozenset, encontrar_componentes_fortes(sucessores)), key=sorted
    )
    assert obtido == esperado


def test_componentes_fortes_em_caminho_longo_sem_recursao():
    n = 50_000
    ciclo = {str(v): {str((v + 1) % n)} for v in range(n)}
    assert [len(c) for c in encontrar_componentes_fortes(ciclo)] == [n]


@pytest.mark.parametrize("semente", range(10))
def test_grafo_nao_dirigido_orientado_tem_uma_componente_forte_por_componente(semente):
    grafo = nx.gnm_random_graph(80, 90, seed=semente)
    adjacencia = {str(v): {str(w) for w in grafo[v]} for v in grafo}
    fortes = encontrar_componentes_fortes(orientar_nos_dois_sentidos(adjacencia))
    conexas = [{str(v) for v in c} for c in nx.connected_components(grafo)]
    assert sorted(map(frozenset, fortes), key=sorted) == sorted(
        map(frozenset, conexas), key=sorted
    )


@pytest.mark.parametrize("semente", range(10))
def test_pontes_e_articulacoes_iguais_ao_networkx(semente):
    grafo = nx.gnm_random_graph(80, 100, seed=semente)
    adjacencia = {str(v): {str(w) for w in grafo[v]} for v in grafo}
    resultado = encontrar_pontes_e_articulacoes(adjacencia)
    pontes = {tuple(sorted((str(p), str(q)))) for p, q in nx.bridges(grafo)}
    articulacoes = {str(v) for v in nx.articulation_points(grafo)}
    assert resultado.pontes == pontes
    assert resultado.articulacoes == articulacoes
