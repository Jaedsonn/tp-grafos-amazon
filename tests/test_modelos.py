"""Propriedades conhecidas dos modelos clássicos gerados com código próprio."""

import statistics

import pytest

from src.parte1.topologia import (
    calcular_clusterizacao_local,
    contar_triangulos_por_vertice,
)
from src.parte3.lei_potencia import ajustar_lei_de_potencia
from src.parte3.modelos import gerar_barabasi_albert, gerar_watts_strogatz
from src.parte3.pequeno_mundo import gerar_erdos_renyi


def clusterizacao_media(adjacencia):
    triangulos = contar_triangulos_por_vertice(adjacencia)
    return statistics.fmean(
        calcular_clusterizacao_local(adjacencia, triangulos).values()
    )


def test_barabasi_albert_tem_cauda_pesada_com_gama_perto_de_tres():
    grafo = gerar_barabasi_albert(20_000, 3, 1)
    graus = [len(v) for v in grafo.values()]
    assert min(graus) == 3
    assert max(graus) > 20 * statistics.fmean(graus)
    assert 2.5 < ajustar_lei_de_potencia(graus).gama < 3.5


def test_barabasi_albert_e_simples_e_simetrico():
    grafo = gerar_barabasi_albert(500, 4, 2)
    for v, vizinhos in grafo.items():
        assert v not in vizinhos
        assert all(v in grafo[w] for w in vizinhos)


@pytest.mark.parametrize("k", [4, 10])
def test_anel_sem_religacao_tem_clusterizacao_teorica(k):
    esperado = 3 * (k - 2) / (4 * (k - 1))
    assert clusterizacao_media(gerar_watts_strogatz(400, k, 0.0, 3)) == pytest.approx(
        esperado
    )


@pytest.mark.parametrize("p", [0.0, 0.1, 1.0])
def test_watts_strogatz_preserva_o_numero_de_arestas(p):
    grafo = gerar_watts_strogatz(1_000, 6, p, 4)
    assert sum(len(v) for v in grafo.values()) // 2 == 3_000
    assert all(v not in vizinhos for v, vizinhos in grafo.items())


def test_religar_derruba_a_clusterizacao_ate_o_nivel_do_aleatorio():
    anel = clusterizacao_media(gerar_watts_strogatz(2_000, 10, 0.0, 5))
    pequeno_mundo = clusterizacao_media(gerar_watts_strogatz(2_000, 10, 0.1, 5))
    aleatorio = clusterizacao_media(gerar_watts_strogatz(2_000, 10, 1.0, 5))
    referencia = clusterizacao_media(gerar_erdos_renyi(2_000, 10_000, 5))
    assert anel > pequeno_mundo > 0.4 > 0.05 > aleatorio
    assert aleatorio == pytest.approx(referencia, abs=0.01)
