import gzip
from dataclasses import dataclass
from pathlib import Path

from src.comum import config
from src.comum.exportacao import (
    escrever_arestas_csv,
    escrever_componentes_csv,
    escrever_funil_csv,
    escrever_jogos_csv,
)
from src.etl.funil import (
    LADO_JOGO,
    contar_graus,
    deduplicar,
    filtrar_jogos_raros,
    filtrar_usuarios_vorazes,
    resumir_bipartido,
)
from src.comum.grafo import (
    componentes_conexas,
    contar_tamanhos_componentes,
    montar_adjacencia,
    restringir_arestas,
)
from src.etl.leitura import ler_catalogo_jogos, ler_pares_avaliacao
from src.etl.projecao import (
    agrupar_por_usuario,
    podar_arestas_fracas,
    projetar_coavaliacao,
    resumir_projecao,
)
from src.comum.tipos import EtapaFunil, ParAvaliacao, PesosArestas


@dataclass(frozen=True)
class GrafoFinal:
    """Resultado do ETL"""

    pesos: PesosArestas
    graus_bipartidos: dict[str, int]
    etapas: list[EtapaFunil]
    tamanhos_componentes: dict[int, int]


def tratar_bipartido(
    pares: list[ParAvaliacao], cap_usuario: int, min_avaliacoes: int
) -> tuple[list[ParAvaliacao], list[EtapaFunil]]:
    """
    :param pares: arestas brutas (usuário, jogo)
    :param cap_usuario: maior k_u aceito (T2)
    :param min_avaliacoes: menor k_p aceito (T3)
    :return: arestas tratadas e as etapas 0–3 do funil

    Exemplo:
        >>> tratados, etapas = tratar_bipartido([("u", "a"), ("u", "a")], 50, 1)
        >>> tratados, [e.arestas for e in etapas]
        ([('u', 'a')], [2, 1, 1, 1])
    """
    etapas = [resumir_bipartido("0_bruto", pares)]
    pares = deduplicar(pares)
    etapas.append(resumir_bipartido("1_dedup", pares))
    pares = filtrar_usuarios_vorazes(pares, cap_usuario)
    etapas.append(resumir_bipartido("2_cap_usuario", pares))
    pares = filtrar_jogos_raros(pares, min_avaliacoes)
    etapas.append(resumir_bipartido("3_min_avaliacoes_jogo", pares))
    return pares, etapas


def projetar_ate_lcc(
    pares: list[ParAvaliacao], min_peso: int
) -> tuple[PesosArestas, list[EtapaFunil], dict[int, int]]:
    """
    :param pares: arestas do bipartido já tratado
    :param min_peso: menor peso aceito no backbone (T5)
    :return: arestas da LCC, as etapas 4–6 do funil e os tamanhos das componentes do backbone

    Exemplo:
        >>> pares = [("a", "1"), ("a", "2"), ("a", "3"), ("b", "2"), ("b", "3"), ("c", "3"), ("c", "4")]
        >>> pesos, _, tamanhos = projetar_ate_lcc(pares, 2)
        >>> pesos, tamanhos
        ({('2', '3'): 2}, {2: 1, 1: 2})
    """
    projecao = projetar_coavaliacao(agrupar_por_usuario(pares))
    etapas = [resumir_projecao("4_projecao", projecao)]
    backbone = podar_arestas_fracas(projecao, min_peso)
    etapas.append(resumir_projecao("5_backbone", backbone))
    adjacencia = montar_adjacencia(backbone)
    # o conjunto de vértices é P após T3: jogos sem aresta forte contam como isolados
    tamanhos = contar_tamanhos_componentes(adjacencia, {jogo for _, jogo in pares})
    pesos_lcc = restringir_arestas(backbone, componentes_conexas(adjacencia)[0])
    etapas.append(resumir_projecao("6_lcc", pesos_lcc))
    return pesos_lcc, etapas, tamanhos


def construir_grafo_final(
    pares: list[ParAvaliacao], cap_usuario: int, min_avaliacoes: int, min_peso: int
) -> GrafoFinal:
    """
    :param pares: arestas brutas (usuário, jogo)
    :param cap_usuario: limiar de T2
    :param min_avaliacoes: limiar de T3
    :param min_peso: limiar de T5
    :return: GrafoFinal com LCC, k_p dos vértices da LCC e funil

    Exemplo:
        >>> pares = [("a", "1"), ("a", "2"), ("b", "1"), ("b", "2")]
        >>> construir_grafo_final(pares, 50, 1, 2).graus_bipartidos
        {'1': 2, '2': 2}
    """
    tratados, etapas_bipartido = tratar_bipartido(pares, cap_usuario, min_avaliacoes)
    pesos_lcc, etapas_projecao, tamanhos = projetar_ate_lcc(tratados, min_peso)
    graus = contar_graus(tratados, LADO_JOGO)
    vertices = sorted({v for aresta in pesos_lcc for v in aresta})
    graus_lcc = {v: graus[v] for v in vertices}
    etapas = etapas_bipartido + etapas_projecao
    return GrafoFinal(pesos_lcc, graus_lcc, etapas, tamanhos)


def salvar_saidas(grafo: GrafoFinal, arq_metadados: Path, dir_saida: Path) -> None:
    """
    :param grafo: resultado de construir_grafo_final
    :param arq_metadados: meta_Video_Games.json.gz, para rotular os vértices
    :param dir_saida: pasta de destino (criada se não existir)

    Exemplo:
        salvar_saidas(grafo, config.ARQ_METADADOS, config.DIR_PROCESSADO)
    """
    dir_saida.mkdir(parents=True, exist_ok=True)
    with gzip.open(arq_metadados, "rt", encoding="utf-8") as fluxo:
        catalogo = ler_catalogo_jogos(fluxo)
    with open(dir_saida / "funil.csv", "w", encoding="utf-8") as fluxo:
        escrever_funil_csv(grafo.etapas, fluxo)
    with open(dir_saida / "componentes.csv", "w", encoding="utf-8") as fluxo:
        escrever_componentes_csv(grafo.tamanhos_componentes, fluxo)
    with open(dir_saida / "jogos_lcc.csv", "w", encoding="utf-8", newline="") as fluxo:
        escrever_jogos_csv(grafo.graus_bipartidos, catalogo, fluxo)
    with gzip.open(dir_saida / "arestas_lcc.csv.gz", "wt", encoding="utf-8") as fluxo:
        escrever_arestas_csv(grafo.pesos, fluxo)


def imprimir_funil(etapas: list[EtapaFunil]) -> None:
    """
    :param etapas: passos do funil

    Exemplo:
        >>> imprimir_funil([EtapaFunil("x", None, 3, 2)])
        x                          usuarios=        -  jogos=      3  arestas=        2
    """
    for e in etapas:
        usuarios = "-" if e.usuarios is None else e.usuarios
        print(
            f"{e.nome:<26} usuarios={usuarios:>9}  jogos={e.jogos:>7}  arestas={e.arestas:>9}"
        )


def main() -> None:
    with open(config.ARQ_AVALIACOES, encoding="utf-8", newline="") as fluxo:
        pares = ler_pares_avaliacao(fluxo)
    grafo = construir_grafo_final(
        pares, config.CAP_USUARIO, config.MIN_AVALIACOES_JOGO, config.MIN_PESO
    )
    salvar_saidas(grafo, config.ARQ_METADADOS, config.DIR_PROCESSADO)
    imprimir_funil(grafo.etapas)


if __name__ == "__main__":
    main()
