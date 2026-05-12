"""Module for plotting position changes and starting grids in F1 sessions."""

from fastf1 import plotting
from fastf1.core import Session
from matplotlib import pyplot as plt

from plots.cars import draw_f1_car


def plot_starting_grid(session: Session) -> None:
    """Load the race session results for a specified Grand Prix, extracts
    the final starting grid, and plots an authentic staggered grid visual using car icons.

    Args:
        session (Session): The session of a race.
    """
    plotting.setup_mpl(mpl_timedelta_support=False, color_scheme="fastf1")
    session.load(telemetry=False, weather=False, messages=False)

    results = session.results.copy()

    grid_drivers = results[results["GridPosition"] > 0].sort_values(by="GridPosition")
    pitlane_drivers = results[results["GridPosition"] == 0]

    x_spacing = 1.5
    y_spacing = 1.3
    stagger_offset = 0.45

    n_cars = len(grid_drivers)
    n_cols = (n_cars + 1) // 2

    x_max = (n_cols - 1) * x_spacing
    max_x = x_max + stagger_offset

    _, ax = plt.subplots(figsize=(max(12, n_cols * 1.6), 5))

    for _, row in grid_drivers.iterrows():
        pos = int(row["GridPosition"])
        driver = row["Abbreviation"]

        color_str = str(row["TeamColor"])
        team_color = f"#{color_str}" if color_str and color_str != "nan" else "#888888"

        grid_col = (pos - 1) // 2
        grid_row = (pos - 1) % 2

        x = x_max - grid_col * x_spacing

        if grid_row == 0:
            x += stagger_offset

        y = (0.5 - grid_row) * y_spacing

        draw_f1_car(ax, x, y, team_color, f"P{pos} {driver}", scale=0.6)

    if not pitlane_drivers.empty:
        pit_x = -1.5
        pit_text = "Pit Lane:\n" + ", ".join(pitlane_drivers["Abbreviation"].tolist())
        ax.text(
            pit_x,
            0,
            pit_text,
            ha="center",
            va="center",
            fontsize=9,
            color="#bbbbbb",
            fontstyle="italic",
            bbox={
                "boxstyle": "square,pad=0.5",
                "facecolor": "#222222",
                "edgecolor": "red",
                "alpha": 0.8,
            },
        )

    x_line = max_x + 0.9
    ax.axvline(
        x=x_line, color="white", linewidth=2.5, linestyle="--", zorder=2, alpha=0.7
    )
    ax.text(
        x_line + 0.05,
        0,
        "START",
        va="center",
        ha="left",
        fontsize=9,
        color="white",
        fontfamily="monospace",
        rotation=90,
    )

    ax.set_title(
        f"{session.event.year} {session.event.EventName}\nStarting Grid",
        pad=20,
    )

    x_left = -2.2 if not pitlane_drivers.empty else -1.0
    ax.set_xlim(x_left, x_line + 0.8)
    ax.set_ylim(-y_spacing, y_spacing)

    ax.axis("off")
    ax.set_aspect("equal")
    plt.tight_layout()
    plt.show()


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
    ax.set_title(f"Position changes during the {session.event.year} {session.event.EventName}")
    plt.tight_layout()

    plt.show()
