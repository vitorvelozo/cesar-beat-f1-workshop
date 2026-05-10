"""Aggregates functions to check whether a distribution is normal."""

import matplotlib.pyplot as plt
import seaborn as sns
from pandas import Series
from scipy.stats import probplot, shapiro

F1_RED = "#FF1801"

def shapiro_wilk_test(data: Series, alpha: float = 0.05) -> bool:
    """Check if the series follows normal distribtuion."""
    statistic, p_value = shapiro(data)

    print(f"Test stastic {statistic:.4f}")
    print(f"P-Value {p_value:.4f}")

    if p_value > alpha:
        print("The data looks normally distributed")
        return True
    print("The data does NOT look normally distributed.")
    return False


def plot_normality_visual_inspection(data: Series) -> None:
    _, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.histplot(data, kde=True, ax=axes[0], color=F1_RED, alpha=1.0)
    axes[0].set_title("Histogram")

    axes[0].get_lines()[0].set_color("white")

    probplot(data, dist="norm", plot=axes[1])
    axes[1].set_title("Q-Q Plot")

    qq_lines = axes[1].get_lines()

    qq_lines[1].set_color("white")

    qq_lines[0].set_color(F1_RED)
    qq_lines[0].set_alpha(0.75)

    plt.tight_layout()
    plt.show()
