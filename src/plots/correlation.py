import matplotlib.pyplot as plt
from numpy import linspace, polyfit
from pandas import Series

def plot_scatter(
    x: Series,
    y: Series,
    title: str = None,
    color: str = "#f691fa",
) -> None:
    """Plot a scatter plot of two series with a regression line."""
    _, ax = plt.subplots(figsize=(12, 5))

    aligned_x, aligned_y = x.align(y, join="inner")

    ax.scatter(aligned_x, aligned_y, color=color, alpha=0.5, s=20)

    m, b = polyfit(aligned_x, aligned_y, 1)
    x_line = linspace(aligned_x.min(), aligned_x.max(), 200)
    ax.plot(x_line, m * x_line + b, color="#36cfba", linewidth=2)

    ax.set_xlabel(x.name or "X", fontsize=11)
    ax.set_ylabel(y.name or "Y", fontsize=11)

    if title:
        ax.set_title(title, fontsize=14)

    plt.tight_layout()
    plt.show()
