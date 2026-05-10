"""Aggregates functions to check statistical differences between distributions."""

from pandas import Series
from scipy.stats import ks_2samp, mannwhitneyu


def ks_test(
    series_a: Series,
    series_b: Series,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Perform a Two-Sample Kolmogorov-Smirnov test."""
    a_clean = Series(series_a).dropna()
    b_clean = Series(series_b).dropna()

    statistic, p_value = ks_2samp(a_clean, b_clean)

    print("=" * 10 + " Kolomogorov-Smirnov test " + "=" * 10)
    print(f"D-Statistic (Max gap between distributions): {statistic:.4f}")
    print(f"P-Value: {p_value:.4f}")

    if p_value < alpha:  # pyright: ignore[reportOperatorIssue]
        print("The distributions are statistically DIFFERENT")
    else:
        print("NO significant difference in distributions")

    return statistic, p_value  # pyright: ignore[reportReturnType]


def mann_whitney_u_test(
    series1: Series,
    series2: Series,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Perform Mann-Whitney U test."""
    statistic, p_value = mannwhitneyu(series1, series2, alternative="two-sided")

    print("=" * 10 + " Mann-Whitney U test " + "=" * 10)
    print(f"Test statistic {statistic:.4f}")
    print(f"P-Value {p_value:.4f}")

    if p_value > alpha:
        print("There IS a statistically significant difference between the series.")
    else:
        print("There is NOT a statistically significant difference between the series.")
    return statistic, p_value
