"""Incident processing helpers for session data."""

from fastf1.core import Session
from pandas import DataFrame, concat


def get_all_incidents_data(sessions: list[Session]) -> DataFrame:
    """Filter racing incidents and combine occurrences across sessions."""
    target_flags = ["BLACK", "DOUBLE YELLOW", "RED", "YELLOW"]
    all_frames = []

    for session in sessions:
        messages = session.race_control_messages
        mask = messages["Flag"].str.upper().isin(target_flags)
        filtered = messages[mask].copy()
        filtered = filtered.groupby("Lap", as_index=False).count()
        filtered["Year"] = session.event.year
        all_frames.append(filtered)

    return concat(all_frames, ignore_index=True)
