"""Module for plotting position changes in F1 sessions."""

from fastf1 import plotting
from fastf1.core import Session
from matplotlib import pyplot as plt


def plot_position_changes(session: Session) -> None:
    """Plot position changes for each driver in a session.

    Args:
        session: A FastF1 session object containing driver lap data.
    """
    _, ax = plt.subplots(figsize=(10, 6))

    for driver in session.drivers:
        driver_laps = session.laps.pick_drivers(driver)

        abbreviation = driver_laps.Driver.iloc[0]
        style = plotting.get_driver_style(
            identifier=abbreviation,
            style=["color", "linestyle"],
            session=session,
        )

        ax.plot(
            driver_laps.LapNumber,
            driver_laps.Position,
            label=abbreviation,
            **style,
        )

    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel("Lap")
    ax.set_ylabel("Position")

    ax.legend(bbox_to_anchor=(1.0, 1.02))
    plt.tight_layout()

    plt.show()
