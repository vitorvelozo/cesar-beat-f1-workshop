"""Reusable functions related to tyre compound and wear analysis."""

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fastf1 import plotting
from fastf1.core import Session
from pandas import DataFrame

from tests.normality import F1_RED

plotting.setup_mpl(mpl_timedelta_support=True, color_scheme="fastf1")


def plot_laptime_distribution_by_team_with_tyre_life(
    data: pd.DataFrame,
    session: Any,
) -> None:
    """Plot lap time distribution by team with tyre life overlay.

    Args:
        data: DataFrame containing lap times, teams, and tyre life information.
        session: FastF1 session object for team color retrieval.

    """
    median_order = data.groupby("Team")["LapTime_s"].median().sort_values().index
    team_palette = {
        team: plotting.get_team_color(team, session=session) for team in median_order
    }

    bins = [-1, 5, 10, 15, 20, 25]
    labels = ["0-5", "6-10", "11-15", "16-20", "21-25"]

    data["TyreLifeCat"] = pd.cut(data["TyreLife"], bins=bins, labels=labels)

    plt.subplots(figsize=(18, 5))

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

    plt.legend(title="Tyre life (laps)", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.title("Lap time distribution by team (shaded by tyre life)")
    plt.ylabel("Lap time (seconds)", fontsize=12)
    plt.tight_layout()
    plt.show()


def plot_tyre_decay_scatter_plot(
    data: pd.DataFrame,
    hue: str = "Session",
) -> None:
    """Plot tyre degradation as a scatter plot with optional KDE overlay.

    Args:
        data: DataFrame containing tyre wear and lap time information.
        kde: Whether to overlay a 2D KDE plot on the scatter plot.
        hue: Column name used to color the points.

    """
    plt.figure(figsize=(10, 5))

    sns.scatterplot(
        data=data,
        x="TyreLife",
        y="LapTime_s",
        hue=hue,
        alpha=0.7,
        s=50,
    )

    title_str = "Tyre degradation: Lap times as tyre life increases "
    title_str += f"({data['Compound'].iloc[0].lower()} compound)"

    plt.title(
        title_str,
        fontsize=14,
    )
    plt.xlabel("Tyre life (laps)", fontsize=12)
    plt.ylabel("Lap time (seconds)", fontsize=12)

    plt.tight_layout()
    plt.show()


def plot_average_lap_time_by_tyre_wear(
    data: pd.DataFrame,
    compound: str,
    session: Any,
) -> None:
    """Plot average lap time by tyre wear for a given compound and session.

    Args:
        data: DataFrame containing tyre life and lap time data.
        compound: Tyre compound name used in the plot title.
        session: Session name used in the plot title.

    """
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

    title_str = f"Average {session.session_info['Name'].lower()} lap time by tyre life "
    title_str += f"({compound.lower()} compound)"

    plt.title(
        title_str,
        fontsize=14,
    )
    plt.xlabel("Tyre life (laps)", fontsize=12)
    plt.ylabel("Average lap time (seconds)", fontsize=12)

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


def plot_tyre_strategy(drivers: DataFrame, stints: DataFrame, session: Session) -> None:
    """Plot tyre strategy for drivers in a session.

    Args:
        drivers: List or iterable of driver names.
        stints: DataFrame containing stint information.
        session: FastF1 session object.

    """
    _, ax = plt.subplots(figsize=(5, 10))

    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]

        previous_stint_end = 0
        for _, row in driver_stints.iterrows():
            compound_color = plotting.get_compound_color(
                row["Compound"],
                session=session,
            )
            plt.barh(
                y=driver,
                width=row["StintLength"],
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black",
                fill=True,
            )

            previous_stint_end += row["StintLength"]

    plt.title("2025 Qatar Grand Prix")
    plt.xlabel("Lap Number")
    ax.invert_yaxis()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.show()
