"""Module for comparing statistics using hypothesis tests."""

from typing import Any

from pandas import DataFrame, unique


def compare_team_series_to_overall_series(
    hypothesis_test: Any,
    data: DataFrame,
    team: str,
    column: str,
) -> None:
    """Compare a team's series against all other teams' series using a hypothesis test.

    Args:
        hypothesis_test: Test function to apply for comparisons.
        data: DataFrame containing data from all teams.
        team: Team name to compare.
        column: Column name to extract for comparison.

    """
    team_series = data.pick_teams(team)[column]

    for current_team in unique(data.Team):
        if current_team == team:
            continue
        print(f"Comparing against {current_team}")
        current_team_series = data.pick_teams(team)[column]
        hypothesis_test(team_series, current_team_series)
        print()
