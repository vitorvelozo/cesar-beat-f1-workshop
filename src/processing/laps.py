"""Module for processing and analyzing lap data."""

from collections.abc import Callable
from typing import Any

import fastf1 as ff1
from fastf1 import plotting
from pandas import DataFrame, isna, to_numeric


def _format_delta(val: Any) -> str | None:
    return None if isna(val) else val


def get_means_for_laps(push_laps: DataFrame) -> tuple[float, float]:
    """Get mean and std for a given set of laps."""
    mean_laps = push_laps["LapTime"].dt.total_seconds().mean()
    std_laps = push_laps["LapTime"].dt.total_seconds().std()
    return mean_laps, std_laps


def get_tyre_life_stats(
    data: DataFrame,
    session: str | None = None,
    delta_formatter: Callable[[float], Any] = _format_delta,
) -> DataFrame:
    """Calculate mean lap times by tyre life with optional session filtering.

    Args:
        data: DataFrame containing lap data, including 'Session', 'TyreLife', and
        'LapTime_s'.
        session: Optional session name to filter laps before aggregation.
        delta_formatter: Callable to format the delta between consecutive mean lap
        times.

    """
    filtered_df = data.copy()
    if session:
        filtered_df = data[data["Session"] == session]

    stats_df = filtered_df.groupby("TyreLife")["LapTime_s"].mean().reset_index()

    stats_df["Delta"] = stats_df["LapTime_s"].diff().apply(delta_formatter)

    return stats_df


def _extract_starting_grid(
    results: DataFrame,
    laps: DataFrame,
    year: int,
    gp: str,
) -> tuple[list[list[str]], list[list[str]], dict[str, Any]]:
    """Parse session results to extract starting grid positions and initial compounds."""
    results_clean = results.copy()
    results_clean["GridPosition"] = to_numeric(
        results_clean["GridPosition"],
        errors="coerce",
    ).fillna(99)
    results_clean = results_clean.sort_values(by="GridPosition").reset_index(drop=True)

    grid_data = []
    pit_lane_starters = []

    for _, row in results_clean.iterrows():
        driver_code = row["Abbreviation"]
        team_name = row["TeamName"]
        grid_pos = row["GridPosition"]

        driver_laps = laps[laps["Driver"] == driver_code]
        start_tyre = (
            str(driver_laps.iloc[0]["Compound"]) if not driver_laps.empty else "UNK"
        )

        if grid_pos in (99, 0):
            pit_lane_starters.append(["Pit Lane", driver_code, team_name, start_tyre])
        else:
            grid_data.append([str(int(grid_pos)), driver_code, team_name, start_tyre])

    grid_data.extend(pit_lane_starters)

    # Initialize the first stop (Stop 0)
    grid_stop = {
        "type": "grid",
        "title": f"{year} {gp} Grand Prix  |  Official Starting Grid",
        "grid_data": grid_data,
        "flag": "GREEN",
    }

    # Generate the fallback buffer data for Lap 1 incidents
    base_table = [[row[0], row[1], row[2], row[3], "Grid"] for row in grid_data]
    base_plot = [(row[1], 0.0, "#555555") for row in grid_data]

    return base_table, base_plot, grid_stop


def _process_lap_data(
    current_laps: DataFrame,
    leader_time: Any,
    session: Any,
) -> tuple[list[list[str]], list[tuple[str, float, str]]]:
    """Compute standing positions, gaps, intervals, and visual plot deltas for a single lap."""
    table_data = []
    plot_data = []

    for idx, row in current_laps.iterrows():
        driver_str = row["Driver"]
        team_str = row["Team"]
        tyre_str = str(row["Compound"])

        if idx == 0:
            gap_str = "Leader"
        else:
            time_ahead = current_laps.iloc[idx - 1]["Time"]
            interval_delta = row["Time"] - time_ahead
            gap_str = f"+{interval_delta.total_seconds():.3f}"

        leader_delta_sec = (row["Time"] - leader_time).total_seconds()

        try:
            color = plotting.get_team_color(row["Team"], session=session)
        except Exception:
            color = "#888888"

        table_data.append([str(idx + 1), driver_str, team_str, tyre_str, gap_str])
        plot_data.append((driver_str, leader_delta_sec, color))

    return table_data, plot_data


def load_race_timeline(
    year: int,
    gp: str,
    event: str,
) -> list[dict[str, Any]]:
    """Load session data and build the complete chronological timeline of stops."""
    ff1.Cache.enable_cache("src/cache")
    session = ff1.get_session(year, gp, event)
    session.load(weather=False)

    laps = session.laps
    rcm = session.race_control_messages
    t0_date = session.t0_date
    total_laps = int(laps["LapNumber"].max())

    last_table_data, last_plot_data, grid_stop = _extract_starting_grid(
        session.results,
        laps,
        year,
        gp,
    )

    timeline_stops = [grid_stop]
    current_flag_status = None

    # Chronological lap processing
    for lap_num in range(1, total_laps + 1):
        current_laps = laps[laps["LapNumber"] == lap_num].dropna(subset=["Time"])
        if current_laps.empty:
            continue

        current_laps = current_laps.sort_values(by="Time").reset_index(drop=True)
        leader_time = current_laps.iloc[0]["Time"]
        lap_end_time = t0_date + current_laps["Time"].max()

        if lap_num > 1:
            lap_start_time = t0_date + (leader_time - current_laps.iloc[0]["LapTime"])
        else:
            lap_start_time = t0_date + session.session_start_time

        # Check for Mid-Lap Flag Incidents
        lap_flags = rcm[
            (rcm["Time"] >= lap_start_time)
            & (rcm["Time"] <= lap_end_time)
            & (rcm["Category"] == "Flag")
        ].sort_values(by="Time")

        for _, flag_row in lap_flags.iterrows():
            current_flag_status = str(flag_row["Message"])
            timeline_stops.append(
                {
                    "type": "flag",
                    "lap": lap_num,
                    "title": f"Lap {lap_num} Incident  |  FLAG: {current_flag_status}",
                    "table": last_table_data,
                    "plot": last_plot_data,
                    "flag": current_flag_status,
                },
            )

        # Compute Regular Lap Completion Standings
        table_data, plot_data = _process_lap_data(current_laps, leader_time, session)

        timeline_stops.append(
            {
                "type": "lap",
                "lap": lap_num,
                "title": f"Lap {lap_num} / {total_laps} Complete  |  Status: {current_flag_status}",
                "table": table_data,
                "plot": plot_data,
                "flag": current_flag_status,
            },
        )

        last_table_data = table_data
        last_plot_data = plot_data

    return timeline_stops
