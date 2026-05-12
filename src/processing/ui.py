"""UI components for visualizing F1 race replay."""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button

BG_COLOR = "#121212"
PANEL_BG_HEADER = "#2a2a2a"
PANEL_BG_ROW = "#1e1e1e"
BORDER_COLOR = "#333333"
AXIS_COLOR = "#444444"
TEXT_MUTED = "#aaaaaa"
TEXT_DEFAULT = "white"

FLAG_COLORS = {
    "YELLOW": "#ffcc00",
    "RED": "#ff3333",
    "GREEN": "#00ff66",
    "CLEAR": "#00ff66",
    "DEFAULT": "white",
}

TYRE_COLORS = {
    "SOFT": "#ff3333",
    "MEDIUM": "#ffcc00",
    "HARD": "#ffffff",
    "INTERMEDIATE": "#33ccff",
    "WET": "#0066ff",
}


class RaceReplayApp:
    def __init__(self, timeline_stops: list[dict], year: int, gp: str) -> None:
        self.timeline_stops = timeline_stops
        self.current_stop_idx = 0
        self.year = year
        self.gp = gp

        # Setup Figure
        plt.style.use("dark_background")
        self.fig = plt.figure(figsize=(12, 8), facecolor=BG_COLOR)
        self.fig.canvas.manager.set_window_title(
            f"F1 Race Replay - {self.year} {self.gp}"
        )

        # Setup Axes grids
        self.ax_plot = plt.subplot2grid((8, 1), (0, 0), rowspan=2)
        self.ax_table = plt.subplot2grid((8, 1), (2, 0), rowspan=5)

        self._setup_buttons()
        self.update_display()

    def _setup_buttons(self) -> None:
        """Instantiate dark-themed UI buttons and hooks up callbacks."""
        self.ax_prev = plt.axes([0.35, 0.02, 0.12, 0.04])
        self.ax_next = plt.axes([0.53, 0.02, 0.12, 0.04])

        self.btn_prev = Button(
            self.ax_prev,
            "< Prev Stop",
            color=PANEL_BG_ROW,
            hovercolor=PANEL_BG_HEADER,
        )
        self.btn_next = Button(
            self.ax_next,
            "Next Stop >",
            color=PANEL_BG_ROW,
            hovercolor=PANEL_BG_HEADER,
        )

        for btn in (self.btn_prev, self.btn_next):
            btn.label.set_color(TEXT_DEFAULT)
            btn.label.set_fontweight("bold")

        for ax in (self.ax_prev, self.ax_next):
            for spine in ax.spines.values():
                spine.set_color(AXIS_COLOR)

        self.btn_prev.on_clicked(self.prev_stop)
        self.btn_next.on_clicked(self.next_stop)
        plt.subplots_adjust(bottom=0.15, hspace=0.4)

    def _get_title_color(self, flag_str: str) -> str:
        """Determine the title header color based on flag keywords."""
        if flag_str:
            flag_upper = flag_str.upper()
            for key, color in FLAG_COLORS.items():
                if key in flag_upper:
                    return color
        return FLAG_COLORS["DEFAULT"]

    def _style_table(self, table, tyre_col_idx: int) -> None:
        """Apply consistent dark-mode styling and tyre compound colors to a table."""
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor(PANEL_BG_HEADER)
                cell.set_text_props(color=TEXT_DEFAULT, weight="bold")
            else:
                cell.set_facecolor(PANEL_BG_ROW)
                # Apply dynamic tyre colors
                if c == tyre_col_idx:
                    val = cell.get_text().get_text().upper()
                    color = next(
                        (v for k, v in TYRE_COLORS.items() if k in val),
                        TEXT_DEFAULT,
                    )
                    cell.set_text_props(color=color)

            cell.set_edgecolor(BORDER_COLOR)

    def update_display(self) -> None:
        """Clear and re-render the plot and table axes based on current state."""
        self.ax_plot.clear()
        self.ax_table.clear()

        self.ax_plot.set_facecolor(BG_COLOR)
        self.ax_table.set_facecolor(BG_COLOR)
        self.ax_plot.axis("off")
        self.ax_table.axis("off")

        stop_data = self.timeline_stops[self.current_stop_idx]
        stop_type = stop_data["type"]

        title_color = self._get_title_color(stop_data["flag"])
        self.fig.suptitle(
            stop_data["title"], fontsize=15, fontweight="bold", color=title_color
        )

        if stop_type == "grid":
            headers = ["Grid Pos", "Driver", "Team", "Start Tyre"]
            table = self.ax_table.table(
                cellText=stop_data["grid_data"],
                colLabels=headers,
                cellLoc="center",
                bbox=[0.20, 0.05, 0.6, 0.95],
            )
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            self._style_table(table, tyre_col_idx=3)

        else:
            # Render Straight-Line Relative Track Positions
            self.ax_plot.axis("on")
            for spine in ("top", "right", "left"):
                self.ax_plot.spines[spine].set_visible(False)
            self.ax_plot.spines["bottom"].set_color(AXIS_COLOR)
            self.ax_plot.tick_params(colors=TEXT_MUTED)
            self.ax_plot.axhline(0, color=AXIS_COLOR, linestyle="--", alpha=0.7)

            max_gap = 0
            for driver, gap_to_leader, color in stop_data["plot"]:
                x_pos = -gap_to_leader
                self.ax_plot.plot(
                    x_pos,
                    0,
                    marker="o",
                    markersize=12,
                    color=color,
                    markeredgecolor="white",
                    markeredgewidth=1.2,
                )
                self.ax_plot.text(
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

            self.ax_plot.set_ylim(-0.2, 0.5)
            self.ax_plot.set_xlim(-max_gap - 5, 5)
            self.ax_plot.get_yaxis().set_visible(False)
            self.ax_plot.set_xlabel("Delta to Leader (Seconds)", color=TEXT_MUTED)
            self.ax_plot.set_title(
                "Relative Track Positions (Straight Line Representation)",
                color="#888888",
                fontsize=10,
            )

            # Render Standings Table
            headers = ["Pos", "Driver", "Team", "Tyre", "Interval"]
            table = self.ax_table.table(
                cellText=stop_data["table"],
                colLabels=headers,
                cellLoc="center",
                bbox=[0.15, 0, 0.7, 0.9],
            )
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            self._style_table(table, tyre_col_idx=3)

        self.fig.canvas.draw_idle()

    def next_stop(self, event=None) -> None:
        if self.current_stop_idx < len(self.timeline_stops) - 1:
            self.current_stop_idx += 1
            self.update_display()

    def prev_stop(self, event=None) -> None:
        if self.current_stop_idx > 0:
            self.current_stop_idx -= 1
            self.update_display()

    def show(self) -> None:
        plt.show()
