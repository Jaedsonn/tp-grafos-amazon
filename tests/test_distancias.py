"""Distâncias exatas próprias contra o NetworkX."""

import networkx as nx
import pytest

from src.parte1.distancias import calcular_distancias_exatas


def para_adjacencia(grafo: nx.Graph) -> dict[str, set[str]]:
    return {str(v): {str(w) for w in grafo[v]} for v in grafo}


@pytest.mark.parametrize("semente", range(8))
def test_distancias_iguais_ao_networkx(semente):
    grafo = nx.connected_watts_strogatz_graph(120, 4, 0.2, seed=semente)
    obtido = calcular_distancias_exatas(para_adjacencia(grafo))
    assert obtido.diametro == nx.diameter(grafo)
    assert obtido.raio == nx.radius(grafo)
    assert obtido.caminho_medio == pytest.approx(nx.average_shortest_path_length(grafo))
    assert sorted(obtido.centro) == sorted(str(v) for v in nx.center(grafo))


def test_processos_paralelos_dao_o_mesmo_resultado():
    adjacencia = para_adjacencia(nx.connected_watts_strogatz_graph(300, 6, 0.1, seed=7))
    assert calcular_distancias_exatas(adjacencia, 2) == calcular_distancias_exatas(
        adjacencia, 1
    )


def test_grafo_desconexo_e_recusado():
    with pytest.raises(ValueError):
        calcular_distancias_exatas({"a": {"b"}, "b": {"a"}, "c": set()})
