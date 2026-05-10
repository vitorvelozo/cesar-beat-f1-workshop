"""Reusable functions related to tyre compound and wear analysis."""

from typing import Any

import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fastf1 import plotting

from tests.normality import F1_RED

ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme="fastf1")

def plot_laptime_distribution_by_team_with_tyre_life(data: pd.DataFrame, session: Any) -> None:
    median_order = data.groupby("Team")["LapTime_s"].median().sort_values().index
    team_palette = {team: plotting.get_team_color(team, session=session) for team in median_order}

    bins = [-1, 5, 10, 15, 20, 25]
    labels = ["0-5", "6-10", "11-15", "16-20", "21-25"]

    data["TyreLifeCat"] = pd.cut(data["TyreLife"], bins=bins, labels=labels)

    fig, ax = plt.subplots(figsize=(18, 5))

    sns.violinplot(
        data=data,
        x="Team",
        y="LapTime_s",
        hue="Team",
        inner=None,
        density_norm="area",
        order=median_order,
        palette=team_palette,
    )

    sns.swarmplot(
        data=data,
        x="Team",
        y="LapTime_s",
        order=median_order,
        hue="TyreLifeCat",
        palette="Greys",
        linewidth=0.5,
        edgecolor="gray",
        size=4,
    )

    plt.legend(title="Tyre Life (Laps)", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.title("Lap Time Distribution by Team (Shaded by Tyre Life)")
    plt.tight_layout()
    plt.show()


def plot_tyre_decay_scatter_plot(data, kde: bool = False, hue: str = "FreshTyre") -> None:
    plt.figure(figsize=(10, 5))

    if kde:
        sns.kdeplot(
            data=data,
            x="TyreLife",
            y="LapTime_s",
            hue=hue,
            fill=True,
            alpha=0.3,
            levels=5,
            thresh=0.1,
            legend=False,
        )

    sns.scatterplot(
        data=data,
        x="TyreLife",
        y="LapTime_s",
        hue=hue,
        alpha=0.7,
        s=50,
    )

    plt.title(f"Tyre Degradation: Lap Time vs. Tyre Life ({data["Compound"].iloc[0].capitalize()} Tyres)", fontsize=14)
    plt.xlabel("Tyre Life (Laps)", fontsize=12)
    plt.ylabel("Lap Time (Seconds)", fontsize=12)

    plt.tight_layout()
    plt.show()

def plot_average_lap_time_by_tyre_wear(
    data: pd.DataFrame, compound: str, session
) -> None:
    plt.figure(figsize=(18, 6))

    ax = sns.lineplot(
        data=data,
        x="TyreLife",
        y="LapTime_s",
        marker="o",
        color=F1_RED,
        linewidth=2.5,
        markersize=8,
    )


    y_range = data["LapTime_s"].max() - data["LapTime_s"].min()
    y_offset = y_range * 0.03

    for _, row in data.iterrows():
        x_coord = row["TyreLife"]
        y_coord = row["LapTime_s"]
        delta_val = row["Delta"]

        if pd.isna(delta_val) or str(delta_val).lower() == "nan":
            continue

        text_color = "yellow" if delta_val >= 0 else "lime"
        text_str = f"{delta_val:+.3f}"

        ax.text(
            x=x_coord,
            y=y_coord + y_offset,
            s=text_str,
            color=text_color,
            fontsize=10,
            ha="left",
            va="bottom",
        )

    plt.title(
        f"Average {session} Lap Time by Tyre Life ({compound.capitalize()} Compound)",
        fontsize=14,
    )
    plt.xlabel("Tyre Life (Laps)", fontsize=12)
    plt.ylabel("Average Lap Time (Seconds)", fontsize=12)

    min_lap = int(data["TyreLife"].min())
    max_lap = int(data["TyreLife"].max())
    plt.xticks(range(min_lap, max_lap + 1))

    plt.ylim(
        data["LapTime_s"].min() - y_offset,
        data["LapTime_s"].max() + (y_offset * 3),
    )

    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
