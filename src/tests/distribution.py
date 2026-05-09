"""Aggregates functions to check statistically significant differences between distributions."""

from pandas import Series
from scipy.stats import ks_2samp, mannwhitneyu


def ks_test(series_a: Series, series_b: Series, alpha: float = 0.05):
    """Perform a Two-Sample Kolmogorov-Smirnov test."""

    a_clean = Series(series_a).dropna()
    b_clean = Series(series_b).dropna()

    statistic, p_value = ks_2samp(a_clean, b_clean)

    print(f"D-Statistic (Max gap between distributions): {statistic:.4f}")
    print(f"P-Value: {p_value:.4f}")

    if p_value < alpha:
        print("Conclusion: The distributions are statistically DIFFERENT (Reject Null).")
    else:
        print("Conclusion: No significant difference in distributions (Fail to Reject Null).")

    return statistic, p_value


def mann_whitney_u_test(series1: Series, series2: Series, alpha: float = 0.05) -> bool:
    """Perform Mann-Whitney U test."""
    
    statistic, p_value = mannwhitneyu(series1, series2, alternative="two-sided")

    print(f"Test stastic {statistic:.4f}")
    print(f"P-Value {p_value:.4f}")

    if p_value > alpha:
        print("There IS a statistically significant difference between the two series.")
        return True
    print("There is NOT a statistically significant difference between the two series.")
    return False
