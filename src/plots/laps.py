"""Aggregates plots for lap data."""

import matplotlib.pyplot as plt
from pandas import DataFrame, isna, merge
from seaborn import heatmap, lineplot


def plot_laptime_correlation_heatmap(data: DataFrame) -> None:
    """Plot correlations between LapTime and other variables."""
    df_numeric = data.copy()
    df_numeric = df_numeric.select_dtypes(include=["float64", "int64"])

    corr_matrix = df_numeric.corr()

    plt.figure(figsize=(12, 10))

    heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        vmin=-1, vmax=1,
        center=0,
        linewidths=0.5,
        cbar_kws={"shrink": .8},
    )

    plt.title("Formula 1 Telemetry: Correlation Heatmap", fontsize=16, pad=20)
    plt.tight_layout()
    plt.show()

    if "LapTime_s" in corr_matrix.columns:
        print("\n--- Correlations with LapTime_s ---")
        laptime_corr = corr_matrix["LapTime_s"].sort_values(ascending=False)
        print(laptime_corr.drop("LapTime_s"))


def plot_team_vs_overall_tyre_wear(
    overall_data: DataFrame,
    team_data: DataFrame,
    team_name: str,
    compound: str,
    session: str,
    team_color: str = "cyan",
    overall_color: str = "white",
) -> None:
    plt.figure(figsize=(18, 6))

    ax = lineplot(
        data=overall_data,
        x="TyreLife",
        y="LapTime_s",
        marker="o",
        color=overall_color,
        linewidth=2.0,
        markersize=6,
        label="Overall Average",
        linestyle="--",
        alpha=0.7,
    )

    lineplot(
        data=team_data,
        x="TyreLife",
        y="LapTime_s",
        marker="o",
        color=team_color,
        linewidth=2.5,
        markersize=8,
        label=team_name,
        ax=ax,
    )

    merged = merge(
        team_data,
        overall_data,
        on="TyreLife",
        suffixes=("_team", "_overall"),
    )

    y_max = max(
        overall_data["LapTime_s"].max(), team_data["LapTime_s"].max()
    )
    y_min = min(
        overall_data["LapTime_s"].min(), team_data["LapTime_s"].min()
    )
    y_range = y_max - y_min
    y_offset = (
        y_range * 0.03 if y_range > 0 else 0.1
    )

    for _, row in merged.iterrows():
        x_coord = row["TyreLife"]
        y_coord_team = row["LapTime_s_team"]
        y_coord_overall = row["LapTime_s_overall"]

        diff = y_coord_team - y_coord_overall

        if isna(diff):
            continue

        text_color = "lime" if diff < 0 else "yellow"
        text_str = f"{diff:+.3f}s"

        ax.text(
            x=x_coord,
            y=y_coord_team + y_offset,
            s=text_str,
            color=text_color,
            fontsize=10,
            ha="left",
            va="bottom",
            fontweight="bold",
        )

    plt.title(
        f"{team_name} vs Overall Average {session} Lap Time by Tyre Life ({compound.capitalize()} Compound)",
        fontsize=14,
        pad=15,
    )
    plt.xlabel("Tyre Life (Laps)", fontsize=12)
    plt.ylabel("Average Lap Time (Seconds)", fontsize=12)

    min_lap = int(
        min(overall_data["TyreLife"].min(), team_data["TyreLife"].min())
    )
    max_lap = int(
        max(overall_data["TyreLife"].max(), team_data["TyreLife"].max())
    )
    plt.xticks(range(min_lap, max_lap + 1))

    plt.ylim(y_min - y_offset, y_max + (y_offset * 3))

    plt.legend(frameon=True, facecolor="black", edgecolor="none")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
