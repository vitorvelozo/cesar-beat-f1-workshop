"""Module for comparing statistics using hypothesis tests."""

from typing import Any

from pandas import DataFrame, unique


def compare_team_series_to_overall_series(
    hypothesis_test: Any,
    data: DataFrame,
    team: str,
    column: str,
    **kwargs: Any,
) -> None:
    """Compare a team's series against all other teams' series using a hypothesis test.

    Args:
        hypothesis_test: Test function to apply for comparisons.
        data: DataFrame containing data from all teams.
        team: Team name to compare.
        column: Column name to extract for comparison.

    """
    language = kwargs.get("language", "en")

    text_by_language = {
        "en": "Comparing against {current_team}",
        "pt": "Comparando contra {current_team}",
    }
    team_series = data.pick_teams(team)[column]

    for current_team in unique(data.Team):
        if current_team == team:
            continue
        template = text_by_language.get(language, text_by_language["en"])
        print(template.format(current_team=current_team))
        current_team_series = data.pick_teams(current_team)[column]
        hypothesis_test(team_series, current_team_series, **kwargs)
        print()
