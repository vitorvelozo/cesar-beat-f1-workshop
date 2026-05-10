"""Module for processing and analyzing lap data."""

from collections.abc import Callable
from typing import Any

from pandas import DataFrame, isna


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
