"""Aggregates plots for lap data."""

from typing import Literal

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from fastf1 import plotting
from fastf1.core import Session
from numpy import tile
from pandas import DataFrame, isna, merge
from seaborn import boxplot, despine, heatmap, lineplot, swarmplot, violinplot


def _plot_correlation_heatmap(
    data: DataFrame,
    title: str = "Correlation heatmap",
    title_color: str = "white",
) -> DataFrame:
    df_numeric = data.copy()
    df_numeric = df_numeric.select_dtypes(include=["float64", "int64"])

    df_numeric = df_numeric.loc[:, df_numeric.std() > 0]

    corr_matrix = df_numeric.corr()

    plt.figure(figsize=(12, 10))

    heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        vmin=-1,
        vmax=1,
        center=0,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
    )

    plt.title(title, fontsize=16, pad=20, color=title_color)
    plt.tight_layout()
    plt.show()

    return corr_matrix


def plot_position_correlation_heatmap(
    data: DataFrame,
    title: str = "Correlation heatmap",
) -> None:
    """Plot correlations between Position and other variables."""
    corr_matrix = _plot_correlation_heatmap(data, title)

    if "Position" in corr_matrix.columns:
        print("\n--- Correlations with position ---")
        laptime_corr = corr_matrix["Position"].sort_values(ascending=False, key=abs)
        print(f"{laptime_corr.drop('Position').map(lambda x: f'{x:.2f}')}")


def plot_laptime_correlation_heatmap(
    data: DataFrame,
    title: str = "Correlation heatmap",
    title_color: str = "white",
) -> None:
    """Plot correlations between LapTime and other variables."""
    corr_matrix = _plot_correlation_heatmap(data, title, title_color)

    if "LapTime_s" in corr_matrix.columns:
        print("\n--- Correlations with lap time ---")
        laptime_corr = corr_matrix["LapTime_s"].sort_values(ascending=False, key=abs)
        print(f"{laptime_corr.drop('LapTime_s').map(lambda x: f'{x:.2f}')}")


def plot_team_vs_grid_tyre_wear(  # noqa: PLR0913
    grid_data: DataFrame,
    team_data: DataFrame,
    compound: str,
    session: Session,
    overall_color: str = "white",
    language: str = "en",
) -> None:
    """Plot team lap time performance against the overall average by tyre life.

    Args:
        grid_data: DataFrame containing the overall average lap times by tyre life.
        team_data: DataFrame containing the team's lap times by tyre life.
        compound: Tyre compound used for the comparison.
        session: Session name for the plot title.
        overall_color: Color used for the overall average line.
        language: Language for the plot labels ("en" or "pt").
    """

    def _get_title() -> str:
        session_name = session.name.lower()
        compound_name = compound.lower()

        default = f"Selected team vs. Grid average {session_name} lap times by tyre life ({compound_name} compound)"
        text_by_language = {
            "en": default,
            "pt": f"Equipe selecionada vs. Média do grid de tempos de volta na {session_name} por vida do pneu (composto {compound_name})",
        }
        return text_by_language.get(language, default)

    def _get_xlabel() -> str:
        default = "Tyre Life (Laps)"
        text_by_language = {
            "en": default,
            "pt": "Vida do pneu (voltas)",
        }
        return text_by_language.get(language, default)

    def _get_ylabel() -> str:
        default = "Average Lap Time (Seconds)"
        text_by_language = {
            "en": default,
            "pt": "Tempo médio de volta (segundos)",
        }
        return text_by_language.get(language, default)

    def _get_grid_label() -> str:
        default = "Grid average"
        text_by_language = {
            "en": default,
            "pt": "Média do grid",
        }
        return text_by_language.get(language, default)

    def _get_team_label() -> str:
        default = "Team average"
        text_by_language = {
            "en": default,
            "pt": "Média da equipe",
        }
        return text_by_language.get(language, default)

    plt.figure(figsize=(15, 5))

    ax = lineplot(
        data=grid_data,
        x="TyreLife",
        y="LapTime_s",
        marker="o",
        color=overall_color,
        linewidth=2.0,
        markersize=6,
        label=_get_grid_label(),
        linestyle="--",
        alpha=0.7,
    )

    lineplot(
        data=team_data,
        x="TyreLife",
        y="LapTime_s",
        marker="o",
        color=plotting.get_compound_color(compound, session),
        markeredgecolor="#bbbbbb",
        linewidth=2.5,
        markersize=8,
        label=_get_team_label(),
        ax=ax,
    )

    merged = merge(
        team_data,
        grid_data,
        on="TyreLife",
        suffixes=("_team", "_overall"),
    )

    y_max = max(
        grid_data["LapTime_s"].max(),
        team_data["LapTime_s"].max(),
    )
    y_min = min(
        grid_data["LapTime_s"].min(),
        team_data["LapTime_s"].min(),
    )
    y_range = y_max - y_min
    y_offset = y_range * 0.03 if y_range > 0 else 0.1

    for _, row in merged.iterrows():
        x_coord = row["TyreLife"]
        y_coord_team = row["LapTime_s_team"]
        y_coord_overall = row["LapTime_s_overall"]

        diff = y_coord_team - y_coord_overall

        if isna(diff):
            continue

        text_color = "lime" if diff < 0 else "yellow"
        text_str = f"{diff:+.3f}"

        ax.text(
            x=x_coord,
            y=y_coord_team + y_offset,
            s=text_str,
            color=text_color,
            fontsize=10,
            ha="left",
            va="bottom",
            path_effects=[pe.withStroke(linewidth=2, foreground="black")],
        )

    plt.title(
        _get_title(),
        fontsize=14,
        pad=15,
    )
    plt.xlabel(_get_xlabel(), fontsize=12)
    plt.ylabel(_get_ylabel(), fontsize=12)

    min_lap = int(
        min(grid_data["TyreLife"].min(), team_data["TyreLife"].min()),
    )
    max_lap = int(
        max(grid_data["TyreLife"].max(), team_data["TyreLife"].max()),
    )
    plt.xticks(range(min_lap, max_lap + 1))

    plt.ylim(y_min - y_offset, y_max + (y_offset * 3))

    plt.legend(frameon=True, facecolor="black", edgecolor="none")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_lap_time_box_plots(
    laps_data: DataFrame,
    session: Session,
    mode: Literal["Driver", "Team"],
) -> None:
    """Plot box plots of lap times by team or driver for a given session.

    Args:
        laps_data: DataFrame containing lap data with Team, Driver, and LapTime_s columns.
        session: Session object containing session information for the plot title.
        mode: Column to compare lap time to. 'Driver' or 'Team'.

    """
    plot_order = (
        laps_data[[mode, "LapTime_s"]]
        .groupby(mode)
        .median()["LapTime_s"]
        .sort_values()
        .index
    )

    if mode == "Team":
        palette = {
            team: plotting.get_team_color(team, session=session) for team in plot_order
        }
    elif mode == "Driver":
        driver_team_dict = laps_data.set_index("Driver")["Team"].to_dict()
        palette = {
            driver: plotting.get_team_color(team, session=session)
            for driver, team in driver_team_dict.items()
            if driver in plot_order
        }

    _, ax = plt.subplots(figsize=(12, 6))

    boxplot(
        data=laps_data,
        x=mode,
        y="LapTime_s",
        hue=mode,
        order=plot_order,
        palette=palette,
        linecolor="white",
        linewidth=1.5,
        legend=False,
        ax=ax,
    )

    for line in ax.lines:
        if line.get_linestyle() == "-":
            line.set_color("grey")

    plt.title(
        f"{session.event.year} {session.event.EventName} lap time box plots by {mode.lower()}"
    )
    plt.grid(visible=False)

    ax.set(xlabel=None)
    plt.ylabel("Lap time (seconds)")
    plt.tight_layout()
    plt.show()


def plot_driver_lap_time_distributions(
    driver_laps: DataFrame,
    finishing_order: list[str],
    session: Session,
) -> None:
    """Plot lap time distributions for each driver in a session.

    Args:
        driver_laps: DataFrame containing driver lap data.
        finishing_order: Ordered list of drivers by finishing position.
        session: Session object used for title and color mapping.

    """
    _, ax = plt.subplots(figsize=(10, 5))

    driver_laps["LapTime_s"] = driver_laps["LapTime"].dt.total_seconds()

    violinplot(
        data=driver_laps,
        x="Driver",
        y="LapTime_s",
        hue="Driver",
        inner=None,
        density_norm="area",
        order=finishing_order,
        palette=plotting.get_driver_color_mapping(session=session),
    )

    swarmplot(
        data=driver_laps,
        x="Driver",
        y="LapTime_s",
        order=finishing_order,
        hue="Compound",
        palette=plotting.get_compound_mapping(session=session),
        hue_order=["SOFT", "MEDIUM", "HARD"],
        linewidth=0,
        size=4,
    )

    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap time (seconds)")
    ax.set_title(
        f"{session.event.year} {session.event.EventName} lap time distributions",
    )
    despine(left=True, bottom=True)

    plt.tight_layout()
    plt.show()
