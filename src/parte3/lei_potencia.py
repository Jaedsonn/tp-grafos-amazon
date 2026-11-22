import math
from dataclasses import dataclass

import powerlaw

# abaixo disso a cauda tem pontos de menos para o MLE ser estável
MIN_PONTOS_NA_CAUDA: int = 50


@dataclass(frozen=True)
class AjustePotencia:
    """Lei de potência P(k) ∝ k^(−γ) ajustada à cauda k >= k_min"""

    gama: float
    k_min: int
    distancia_ks: float
    n_cauda: int


def estimar_gama(graus: list[int], k_min: int) -> float:
    """
    :param graus: grau de cada vértice
    :param k_min: início da cauda
    :return: γ̂ = 1 + n_cauda / Σ ln(k / (k_min − ½)), o MLE discreto aproximado de Clauset et al. (2009)

    Exemplo:
        >>> round(estimar_gama([2, 2, 4, 8], 2), 3)
        2.238
    """
    cauda = [k for k in graus if k >= k_min]
    soma = sum(math.log(k / (k_min - 0.5)) for k in cauda)
    return 1 + len(cauda) / soma


def medir_distancia_ks(graus: list[int], k_min: int, gama: float) -> float:
    """
    :param graus: grau de cada vértice
    :param k_min: início da cauda
    :param gama: expoente ajustado
    :return: D = max |CCDF empírica − CCDF do modelo| na cauda (estatística de Kolmogorov–Smirnov)

    Exemplo:
        >>> medir_distancia_ks([1, 1, 1, 1], 1, 2.5)
        0.0
    """
    cauda = sorted(k for k in graus if k >= k_min)
    n = len(cauda)
    distancia = 0.0
    for i, k in enumerate(cauda):
        if i > 0 and cauda[i - 1] == k:
            continue
        empirica = (n - i) / n
        # CCDF contínua com correção de ½, coerente com o MLE acima
        modelo = ((k - 0.5) / (k_min - 0.5)) ** (1 - gama)
        distancia = max(distancia, abs(empirica - modelo))
    return distancia


def ajustar_lei_de_potencia(graus: list[int]) -> AjustePotencia:
    """
    :param graus: grau de cada vértice
    :return: AjustePotencia com o k_min que minimiza a distância KS

    Exemplo:
        >>> ajuste = ajustar_lei_de_potencia([1] * 40 + [2] * 20 + [4] * 10 + [8] * 5 + [16] * 2)
        >>> ajuste.k_min, round(ajuste.gama, 2)
        (1, 1.79)
    """
    candidatos = [
        k
        for k in sorted(set(graus))
        if sum(1 for g in graus if g >= k) >= MIN_PONTOS_NA_CAUDA
    ]
    if not candidatos:
        raise ValueError(f"{len(graus)} graus; esperado ao menos {MIN_PONTOS_NA_CAUDA} na cauda")
    melhor: AjustePotencia | None = None
    for k_min in candidatos:
        gama = estimar_gama(graus, k_min)
        distancia = medir_distancia_ks(graus, k_min, gama)
        if melhor is None or distancia < melhor.distancia_ks:
            n_cauda = sum(1 for g in graus if g >= k_min)
            melhor = AjustePotencia(gama, k_min, distancia, n_cauda)
    return melhor


@dataclass(frozen=True)
class ComparacaoDistribuicoes:
    """Teste de razão de verossimilhança do pacote powerlaw (Clauset et al., 2009)"""

    gama: float
    k_min: int
    razao_lognormal: float
    p_lognormal: float


def comparar_distribuicoes(graus: list[int]) -> ComparacaoDistribuicoes:
    """
    :param graus: grau de cada vértice
    :return: γ e k_min do powerlaw, e R, p contra a lognormal;
        R < 0 com p < 0,1 significa que a lognormal explica melhor a cauda

    Exemplo:
        c = comparar_distribuicoes(list(graus.values()))
    """
    ajuste = powerlaw.Fit(graus, discrete=True, verbose=False)
    r_log, p_log = ajuste.distribution_compare("power_law", "lognormal")
    return ComparacaoDistribuicoes(
        float(ajuste.power_law.alpha),
        int(ajuste.power_law.xmin),
        float(r_log),
        float(p_log),
    )
