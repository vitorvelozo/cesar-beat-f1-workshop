from collections.abc import Callable

from pandas import DataFrame


def get_means_for_laps(push_laps: DataFrame) -> tuple[float, float]:
    """Get mean and std for a given set of laps."""
    mean_laps = push_laps["LapTime"].dt.total_seconds().mean()
    std_laps = push_laps["LapTime"].dt.total_seconds().std()
    return mean_laps, std_laps


def get_tyre_life_stats(
    data: DataFrame,
    delta_formatter: Callable[[float], any],
    is_sprint: bool = False,
) -> DataFrame:
    """Filter lap data by session, calculates the mean lap time per tyre life
    and computes the formatted delta between consecutive laps.
    """
    filtered_df = data.copy()
    if is_sprint:
        session_val = 1 if is_sprint else 0
        filtered_df = data[data["Session_Sprint"] == session_val]

    stats_df = (
        filtered_df.groupby("TyreLife")["LapTime_s"]
        .mean()
        .reset_index()
    )

    stats_df["Delta"] = (
        stats_df["LapTime_s"].diff().apply(delta_formatter)
    )

    return stats_df
