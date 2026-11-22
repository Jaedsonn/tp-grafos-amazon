import math
import statistics
from dataclasses import dataclass

from scipy import stats

# acima disto o enunciado manda usar a normal (z); abaixo, t-Student
AMOSTRA_GRANDE: int = 30


@dataclass(frozen=True)
class Estimativa:
    """Média amostral com desvio padrão e intervalo de confiança"""

    media: float
    desvio_padrao: float
    ic_inferior: float
    ic_superior: float
    n: int


def valor_critico(n: int, confianca: float) -> float:
    """
    :param n: tamanho da amostra
    :param confianca: nível de confiança, ex.: 0.95
    :return: z_{α/2} se n >= 30, senão t_{α/2} com n − 1 graus de liberdade

    Exemplo:
        >>> round(valor_critico(30, 0.95), 2), round(valor_critico(10, 0.95), 2)
        (1.96, 2.26)
    """
    quantil = 1 - (1 - confianca) / 2
    if n >= AMOSTRA_GRANDE:
        return float(stats.norm.ppf(quantil))
    return float(stats.t.ppf(quantil, n - 1))


def estimar_media_com_ic(amostras: list[float], confianca: float = 0.95) -> Estimativa:
    """
    :param amostras: observações independentes, ao menos 2
    :param confianca: nível de confiança do intervalo
    :return: Estimativa com média, DP (ddof = 1) e IC

    Exemplo:
        >>> e = estimar_media_com_ic([1.0, 2.0, 3.0])
        >>> e.media, round(e.ic_inferior, 3), round(e.ic_superior, 3)
        (2.0, -0.484, 4.484)
    """
    if len(amostras) < 2:
        raise ValueError(
            f"amostra com {len(amostras)} valor(es): {amostras!r}; esperado ao menos 2"
        )
    media = statistics.fmean(amostras)
    desvio = statistics.stdev(amostras)
    margem = valor_critico(len(amostras), confianca) * desvio / math.sqrt(len(amostras))
    return Estimativa(media, desvio, media - margem, media + margem, len(amostras))
