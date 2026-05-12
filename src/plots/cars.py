"""Module for plotting stylized F1 cars using matplotlib."""

import matplotlib.patheffects as pe
import numpy as np
from matplotlib import patches
from matplotlib.patches import FancyBboxPatch, Polygon


def draw_f1_car(ax, cx, cy, color, label, scale=1.0) -> None:
    """Draw a top-down stylized F1 car centered at (cx, cy).

    Args:
        ax: Matplotlib axes to draw on.
        cx (float): X center of the car.
        cy (float): Y center of the car.
        color (str): Hex color string for the car body (e.g. '#e8002d').
        label (str): Text label drawn inside the car (e.g. 'P1 VER').
        scale (float): Uniform scale factor for the car size.
    """
    s = scale

    def patch(artist) -> None:
        ax.add_patch(artist)

    try:
        import matplotlib.colors as mcolors

        rgb = mcolors.to_rgb(color)
        dark_color = tuple(max(0, c * 0.55) for c in rgb)
        light_color = tuple(min(1, c * 1.3 + 0.15) for c in rgb)
    except Exception:
        dark_color = "#333333"
        light_color = color

    # Rear wing
    rw_w, rw_h = 0.10 * s, 0.70 * s
    patch(
        FancyBboxPatch(
            (cx - 0.52 * s, cy - rw_h / 2),
            rw_w,
            rw_h,
            boxstyle="round,pad=0.02",
            facecolor=dark_color,
            edgecolor="white",
            linewidth=0.6 * s,
            zorder=3,
        )
    )

    # Main body
    body_verts = np.array(
        [
            [cx + 0.60 * s, cy],  # nose tip
            [cx + 0.38 * s, cy - 0.18 * s],  # nose lower shoulder
            [cx + 0.10 * s, cy - 0.22 * s],  # cockpit lower
            [cx - 0.05 * s, cy - 0.28 * s],  # sidepod lower front
            [cx - 0.28 * s, cy - 0.30 * s],  # sidepod lower rear
            [cx - 0.42 * s, cy - 0.22 * s],  # gearbox lower
            [cx - 0.42 * s, cy + 0.22 * s],  # gearbox upper
            [cx - 0.28 * s, cy + 0.30 * s],  # sidepod upper rear
            [cx - 0.05 * s, cy + 0.28 * s],  # sidepod upper front
            [cx + 0.10 * s, cy + 0.22 * s],  # cockpit upper
            [cx + 0.38 * s, cy + 0.18 * s],  # nose upper shoulder
        ]
    )
    patch(
        Polygon(
            body_verts,
            closed=True,
            facecolor=color,
            edgecolor="white",
            linewidth=0.8 * s,
            zorder=4,
        )
    )

    # Front wing
    fw_verts = np.array(
        [
            [cx + 0.60 * s, cy - 0.35 * s],
            [cx + 0.60 * s, cy + 0.35 * s],
            [cx + 0.48 * s, cy + 0.22 * s],
            [cx + 0.48 * s, cy - 0.22 * s],
        ]
    )
    patch(
        Polygon(
            fw_verts,
            closed=True,
            facecolor=dark_color,
            edgecolor="white",
            linewidth=0.6 * s,
            zorder=5,
        )
    )

    # Cockpit
    cockpit = patches.Ellipse(
        (cx + 0.08 * s, cy),
        0.18 * s,
        0.22 * s,
        facecolor="#111111",
        edgecolor="white",
        linewidth=0.5 * s,
        zorder=6,
    )
    patch(cockpit)

    # Halo
    halo = patches.Arc(
        (cx + 0.08 * s, cy),
        0.22 * s,
        0.28 * s,
        angle=90,
        theta1=0,
        theta2=180,
        color="white",
        linewidth=1.2 * s,
        zorder=7,
    )
    ax.add_patch(halo)

    # Tyres
    tyre_color = "#1a1a1a"
    rim_color = "#cccccc"
    tyre_positions = [
        (cx + 0.28 * s, cy - 0.30 * s),  # front lower
        (cx + 0.28 * s, cy + 0.30 * s),  # front upper
        (cx - 0.30 * s, cy - 0.32 * s),  # rear lower
        (cx - 0.30 * s, cy + 0.32 * s),  # rear upper
    ]
    tyre_sizes = [
        (0.11 * s, 0.16 * s),
        (0.11 * s, 0.16 * s),
        (0.12 * s, 0.18 * s),
        (0.12 * s, 0.18 * s),
    ]
    for (tx, ty), (tw, th) in zip(tyre_positions, tyre_sizes):
        patch(
            patches.Ellipse(
                (tx, ty),
                tw,
                th,
                facecolor=tyre_color,
                edgecolor="#555555",
                linewidth=0.5 * s,
                zorder=3,
            )
        )
        patch(
            patches.Ellipse(
                (tx, ty),
                tw * 0.55,
                th * 0.55,
                facecolor=rim_color,
                edgecolor=rim_color,
                linewidth=0,
                zorder=4,
            )
        )

    # Driver label
    parts = label.split(" ", 1)
    pos_text = parts[0] if len(parts) > 1 else ""
    abbr_text = parts[1] if len(parts) > 1 else label

    # Abbreviation
    ax.text(
        cx,
        cy - 0.75 * s,
        abbr_text,
        ha="center",
        va="center",
        fontsize=max(4, 24 * s),
        color="white",
        fontfamily="monospace",
        zorder=10,
        path_effects=[pe.withStroke(linewidth=1.5 * s, foreground="black")],
    )
    # Position number
    ax.text(
        cx + 1 * s,
        cy,
        pos_text,
        ha="center",
        va="center",
        fontsize=max(4, 24 * s),
        color="#dddddd",
        fontfamily="monospace",
        zorder=10,
    )
