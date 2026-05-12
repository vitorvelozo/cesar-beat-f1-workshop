"""Aggregates functions to check whether a distribution is normal."""

import matplotlib.pyplot as plt
import seaborn as sns
from pandas import Series
from scipy.stats import probplot, shapiro


def shapiro_wilk_test(data: Series, alpha: float = 0.05, language: str = "en") -> bool:
    """Check if the series follows normal distribution."""

    def _get_reject_h0() -> str:
        default = "The data does NOT look normally distributed."
        text_by_language = {
            "en": default,
            "pt": "Os dados NÃO parecem normalmente distribuídos.",
        }
        return text_by_language.get(language, default)

    def _get_fail_reject_h0() -> str:
        default = "The data looks normally distributed."
        text_by_language = {
            "en": default,
            "pt": "Os dados parecem normalmente distribuídos",
        }
        return text_by_language.get(language, default)

    statistic, p_value = shapiro(data)

    print(f"Test statistic {statistic:.4f}")
    print(f"P-Value {p_value:.4f}")

    if p_value > alpha:
        print(_get_fail_reject_h0())
        return True
    print(_get_reject_h0())
    return False


def plot_normality_visual_inspection(
    data: Series, title: str = None, color: str = "#f691fa"
) -> None:
    """Plot histogram and Q-Q plot for visual normality inspection."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.histplot(data, kde=True, ax=axes[0], color=color, alpha=1.0)  # pyright: ignore[reportArgumentType]
    axes[0].set_title("Histogram", fontsize=12)

    if axes[0].lines:
        axes[0].lines[-1].set_color("#36cfba")

    probplot(data, dist="norm", plot=axes[1])
    axes[1].set_title("Q-Q Plot", fontsize=12)

    qq_lines = axes[1].get_lines()
    qq_lines[1].set_color("#36cfba")
    qq_lines[0].set_color(color)
    qq_lines[0].set_alpha(0.75)

    if title:
        fig.suptitle(title, fontsize=14)

    plt.tight_layout()
    plt.show()
