"""Module for race replay functionality."""
# This race replay is very ugly and limited. It was made like this because the goal was
# to create a race replay in which users can not obtain information regarding to which
# track is being raced, to avoid them remembering about the actual race and answering
# according to memory rather than data-based decision making.

import os

from processing.laps import load_race_timeline
from processing.ui import RaceReplayApp

YEAR = int(os.getenv("EVENT_YEAR"))
GP_NAME = os.getenv("GP_NAME")


def main() -> None:
    print("Loading data for the race...")
    timeline_stops = load_race_timeline(YEAR, GP_NAME, "R")

    print(f"Successfully loaded {len(timeline_stops)} timeline stops. Launching UI...")
    app = RaceReplayApp(timeline_stops, YEAR, GP_NAME)
    app.show()


if __name__ == "__main__":
    main()
