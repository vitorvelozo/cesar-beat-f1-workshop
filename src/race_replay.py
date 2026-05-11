import fastf1
import matplotlib.pyplot as plt
import pandas as pd
from fastf1 import plotting
from matplotlib.widgets import Button

fastf1.Cache.enable_cache("src/cache")

year, gp, event = 2025, "Qatar", "R"
session = fastf1.get_session(year, gp, event)
session.load(weather=False)

laps = session.laps
rcm = session.race_control_messages
t0_date = session.t0_date

total_laps = int(laps["LapNumber"].max())

# --- Pull True Starting Grid from Session Results ---
results = session.results.copy()
results["GridPosition"] = pd.to_numeric(
    results["GridPosition"], errors="coerce"
).fillna(99)
results = results.sort_values(by="GridPosition").reset_index(drop=True)

grid_data = []
pit_lane_starters = []

for idx, row in results.iterrows():
    driver_code = row["Abbreviation"]
    team_name = row["TeamName"]
    grid_pos = row["GridPosition"]

    # 1. Reliably extract the starting tyre compound from the driver's very first lap
    driver_laps = laps[laps["Driver"] == driver_code]
    if not driver_laps.empty:
        start_tyre = str(driver_laps.iloc[0]["Compound"])
    else:
        start_tyre = "UNK"

    if grid_pos == 99 or grid_pos == 0:
        pit_lane_starters.append(["Pit Lane", driver_code, team_name, start_tyre])
    else:
        grid_data.append([str(int(grid_pos)), driver_code, team_name, start_tyre])

grid_data.extend(pit_lane_starters)

# 2. Build Chronological Timeline of "Stops" (Grid -> Mid-Lap Flags -> Lap Completions)
timeline_stops = []

# Stop 0: Official Starting Grid
timeline_stops.append(
    {
        "type": "grid",
        "title": f"{year} {gp} Grand Prix  |  Official Starting Grid",
        "grid_data": grid_data,
        "flag": "GREEN",
    }
)

current_flag_status = "GREEN"

# Base standings buffer used if a flag is issued on Lap 1 before completion
# Adding an initial gap placeholder "Grid" to match the 5-column layout
last_table_data = [[row[0], row[1], row[2], row[3], "Grid"] for row in grid_data]
last_plot_data = [(row[1], 0.0, "#555555") for row in grid_data]

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

    # --- A. Check for Mid-Lap Flag Incidents ---
    lap_flags = rcm[
        (rcm["Time"] >= lap_start_time)
        & (rcm["Time"] <= lap_end_time)
        & (rcm["Category"] == "Flag")
    ].sort_values(by="Time")

    for _, flag_row in lap_flags.iterrows():
        flag_msg = flag_row["Message"]
        current_flag_status = f"{flag_msg}"

        # Insert a dedicated stop for the flag event using the last stable standings
        timeline_stops.append(
            {
                "type": "flag",
                "lap": lap_num,
                "title": f"Lap {lap_num} Incident  |  FLAG: {current_flag_status}",
                "table": last_table_data,
                "plot": last_plot_data,
                "flag": current_flag_status,
            }
        )

    # --- B. Compute Regular Lap Completion Standings ---
    table_data = []
    plot_data = []

    for idx, row in current_laps.iterrows():
        driver_str = row["Driver"]
        team_str = row["Team"]
        tyre_str = str(row["Compound"])  # Extract the active compound for this lap

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

        # Append data mapped to the 5 columns: Pos, Driver, Team, Tyre, Interval
        table_data.append([str(idx + 1), driver_str, team_str, tyre_str, gap_str])
        plot_data.append((driver_str, leader_delta_sec, color))

    # Insert dedicated stop for the lap completion
    timeline_stops.append(
        {
            "type": "lap",
            "lap": lap_num,
            "title": f"Lap {lap_num} / {total_laps} Complete  |  Status: {current_flag_status}",
            "table": table_data,
            "plot": plot_data,
            "flag": current_flag_status,
        }
    )

    # Update stable buffer for the next iteration
    last_table_data = table_data
    last_plot_data = plot_data


# 3. Build the Matplotlib UI (DARK MODE OVERHAUL)
plt.style.use("dark_background")

fig = plt.figure(figsize=(12, 8), facecolor="#121212")
fig.canvas.manager.set_window_title(f"F1 Race Replay (Dark Mode) - {year} {gp}")

ax_plot = plt.subplot2grid((8, 1), (0, 0), rowspan=2)
ax_table = plt.subplot2grid((8, 1), (2, 0), rowspan=5)

current_stop_idx = 0


def update_display(idx) -> None:
    """Renders the screen based purely on the current chronological stop index."""
    ax_plot.clear()
    ax_table.clear()

    ax_plot.set_facecolor("#121212")
    ax_table.set_facecolor("#121212")
    ax_plot.axis("off")
    ax_table.axis("off")

    stop_data = timeline_stops[idx]
    stop_type = stop_data["type"]
    flag_str = stop_data["flag"]

    # Determine status color dynamically
    title_color = "white"
    if "YELLOW" in flag_str.upper():
        title_color = "#ffcc00"
    elif "RED" in flag_str.upper():
        title_color = "#ff3333"
    elif "GREEN" in flag_str.upper() or "CLEAR" in flag_str.upper():
        title_color = "#00ff66"

    fig.suptitle(
        stop_data["title"],
        fontsize=15,
        fontweight="bold",
        color=title_color,
    )

    if stop_type == "grid":
        # --- Render Grid Screen (Expanded to 4 columns) ---
        headers = ["Grid Pos", "Driver", "Team", "Start Tyre"]
        table = ax_table.table(
            cellText=stop_data["grid_data"],
            colLabels=headers,
            cellLoc="center",
            bbox=[0.20, 0.05, 0.6, 0.95],  # Widened bounding box from 0.5 to 0.6
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        # Apply dark mode table styling
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor("#2a2a2a")
                cell.set_text_props(color="white", weight="bold")
            else:
                cell.set_facecolor("#1e1e1e")

                # Optionally add basic compound coloring text cues
                text_color = "white"
                if c == 3:  # Tyre column
                    val = cell.get_text().get_text()
                    if "SOFT" in val:
                        text_color = "#ff3333"
                    elif "MEDIUM" in val:
                        text_color = "#ffcc00"
                cell.set_text_props(color=text_color)

            cell.set_edgecolor("#333333")

    else:
        # --- Render Race/Incident Screen ---
        ax_plot.axis("on")
        ax_plot.spines["top"].set_visible(False)
        ax_plot.spines["right"].set_visible(False)
        ax_plot.spines["left"].set_visible(False)
        ax_plot.spines["bottom"].set_color("#444444")
        ax_plot.tick_params(colors="#aaaaaa")

        ax_plot.axhline(0, color="#444444", linestyle="--", alpha=0.7)

        max_gap = 0
        for driver, gap_to_leader, color in stop_data["plot"]:
            x_pos = -gap_to_leader

            ax_plot.plot(
                x_pos,
                0,
                marker="o",
                markersize=12,
                color=color,
                markeredgecolor="white",
                markeredgewidth=1.2,
            )
            ax_plot.text(
                x_pos,
                0.06,
                driver,
                fontsize=9,
                ha="center",
                va="bottom",
                rotation=45,
                color="white",
                fontweight="bold",
            )
            max_gap = max(max_gap, gap_to_leader)

        ax_plot.set_ylim(-0.2, 0.5)
        ax_plot.set_xlim(-max_gap - 5, 5)
        ax_plot.get_yaxis().set_visible(False)
        ax_plot.set_xlabel("Delta to Leader (Seconds)", color="#aaaaaa")
        ax_plot.set_title(
            "Relative Track Positions (Straight Line Representation)",
            color="#888888",
            fontsize=10,
        )

        headers = ["Pos", "Driver", "Team", "Tyre", "Interval"]
        table = ax_table.table(
            cellText=stop_data["table"],
            colLabels=headers,
            cellLoc="center",
            bbox=[0.15, 0, 0.7, 0.9],
        )

        table.auto_set_font_size(value=False)
        table.set_fontsize(9)

        # Apply dark mode table styling
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor("#2a2a2a")
                cell.set_text_props(color="white", weight="bold")
            else:
                cell.set_facecolor("#1e1e1e")

                text_color = "white"
                if c == 3:  # Colour code the tyre compounds dynamically
                    val = cell.get_text().get_text()
                    if "SOFT" in val:
                        text_color = "#ff3333"
                    elif "MEDIUM" in val:
                        text_color = "#ffcc00"
                cell.set_text_props(color=text_color)

            cell.set_edgecolor("#333333")

    fig.canvas.draw_idle()


def next_stop(event=None) -> None:
    global current_stop_idx
    if current_stop_idx < len(timeline_stops) - 1:
        current_stop_idx += 1
        update_display(current_stop_idx)


def prev_stop(event=None) -> None:
    global current_stop_idx
    if current_stop_idx > 0:
        current_stop_idx -= 1
        update_display(current_stop_idx)


# Centered Dark Mode Buttons
ax_prev = plt.axes([0.35, 0.02, 0.12, 0.04])
ax_next = plt.axes([0.53, 0.02, 0.12, 0.04])

btn_prev = Button(ax_prev, "< Prev Stop", color="#1e1e1e", hovercolor="#2a2a2a")
btn_next = Button(ax_next, "Next Stop >", color="#1e1e1e", hovercolor="#2a2a2a")

btn_prev.label.set_color("white")
btn_next.label.set_color("white")
btn_prev.label.set_fontweight("bold")
btn_next.label.set_fontweight("bold")

for ax in [ax_prev, ax_next]:
    for spine in ax.spines.values():
        spine.set_color("#444444")

btn_prev.on_clicked(prev_stop)
btn_next.on_clicked(next_stop)

plt.subplots_adjust(bottom=0.15, hspace=0.4)

# Render initial state
update_display(current_stop_idx)
fig.canvas.draw()
plt.show()
