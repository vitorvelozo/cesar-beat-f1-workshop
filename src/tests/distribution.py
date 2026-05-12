"""Aggregates functions to check statistical differences between distributions."""

from pandas import Series
from scipy.stats import ks_2samp, mannwhitneyu


def ks_test(
    series_a: Series,
    series_b: Series,
    alpha: float = 0.05,
    language: str = "en",
) -> tuple[float, float]:
    """Perform a Two-Sample Kolmogorov-Smirnov test."""

    def _get_reject_h0() -> str:
        default = "There IS a statistically significant difference between the series."
        text_by_language = {
            "en": default,
            "pt": "EXISTE uma diferença estatisticamente significativa entre as séries.",
        }
        return text_by_language.get(language, default)

    def _get_fail_reject_h0() -> str:
        default = (
            "There is NOT a statistically significant difference between the series."
        )
        text_by_language = {
            "en": default,
            "pt": "NÃO existe diferença estatisticamente significativa entre as séries.",
        }
        return text_by_language.get(language, default)

    a_clean = Series(series_a).dropna()
    b_clean = Series(series_b).dropna()

    statistic, p_value = ks_2samp(a_clean, b_clean)

    print("=" * 10 + " Kolomogorov-Smirnov " + "=" * 10)
    print(f"D-Statistic (Max gap between distributions): {statistic:.4f}")
    print(f"P-Value: {p_value:.4f}")

    if p_value > alpha:
        print(_get_fail_reject_h0())
    else:
        print(_get_reject_h0())

    return statistic, p_value  # pyright: ignore[reportReturnType]


def mann_whitney_u_test(
    series1: Series,
    series2: Series,
    alpha: float = 0.05,
    language: str = "en",
) -> tuple[float, float]:
    """Perform Mann-Whitney U test."""

    def _get_reject_h0() -> str:
        default = (
            "There is NOT a statistically significant difference between the series."
        )
        text_by_language = {
            "en": default,
            "pt": "NÃO existe diferenca estatisticamente significativa entre as séries.",
        }
        return text_by_language.get(language, default)

    def _get_fail_reject_h0() -> str:
        default = "There IS a statistically significant difference between the series."
        text_by_language = {
            "en": default,
            "pt": "EXISTE uma diferença estatisticamente significativa entre as séries.",
        }
        return text_by_language.get(language, default)

    statistic, p_value = mannwhitneyu(series1, series2, alternative="two-sided")

    print("=" * 10 + " Mann-Whitney U " + "=" * 10)
    print(f"Test statistic {statistic:.4f}")
    print(f"P-Value {p_value:.4f}")

    if p_value > alpha:
        print(_get_fail_reject_h0())
    else:
        print(_get_reject_h0())
    return statistic, p_value
