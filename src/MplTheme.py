"""Matplotlib theme helpers for CompPy (gh #22)."""

from matplotlib.figure import Figure


_DARK = {
    "figure.facecolor": "#232323",
    "axes.facecolor": "#2b2b2b",
    "axes.edgecolor": "#c8c8c8",
    "axes.labelcolor": "#e0e0e0",
    "xtick.color": "#e0e0e0",
    "ytick.color": "#e0e0e0",
    "text.color": "#e0e0e0",
    "grid.color": "#555555",
    "legend.facecolor": "#2b2b2b",
    "legend.edgecolor": "#555555",
}
_LIGHT = {
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.edgecolor": "#222222",
    "axes.labelcolor": "#222222",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    "text.color": "#222222",
    "grid.color": "#cccccc",
    "legend.facecolor": "#ffffff",
    "legend.edgecolor": "#cccccc",
}


def is_dark_mode():
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return True
        for w in app.topLevelWidgets():
            if hasattr(w, "darkMode"):
                return bool(w.darkMode)
            # MainWindow stores darkMode on the UI object attached as .ui in some setups;
            # also check central/parent patterns used by this app.
            ui = getattr(w, "ui", None)
            if ui is not None and hasattr(ui, "darkMode"):
                return bool(ui.darkMode)
        # Fallback: heuristic from palette lightness.
        pal = app.palette()
        return pal.window().color().lightness() < 128
    except Exception:
        return True


def apply_figure_theme(fig, dark=None):
    if dark is None:
        dark = is_dark_mode()
    if not isinstance(fig, Figure):
        return
    style = _DARK if dark else _LIGHT
    fig.set_facecolor(style["figure.facecolor"])
    for ax in fig.get_axes():
        ax.set_facecolor(style["axes.facecolor"])
        for spine in ax.spines.values():
            spine.set_color(style["axes.edgecolor"])
        ax.tick_params(colors=style["xtick.color"], which="both")
        ax.xaxis.label.set_color(style["axes.labelcolor"])
        ax.yaxis.label.set_color(style["axes.labelcolor"])
        ax.title.set_color(style["text.color"])
        # 3D axes have w_* panes in some mpl versions; guard.
        for attr in ("w_xaxis", "w_yaxis", "w_zaxis"):
            axis = getattr(ax, attr, None)
            if axis is not None:
                try:
                    axis.label.set_color(style["axes.labelcolor"])
                    for t in axis.get_ticklabels():
                        t.set_color(style["xtick.color"])
                    axis.line.set_color(style["axes.edgecolor"])
                except Exception:
                    pass
        for pane in ("w_xaxis", "w_yaxis", "w_zaxis"):
            axis = getattr(ax, pane, None)
            if axis is not None and hasattr(axis, "pane"):
                try:
                    axis.pane.set_facecolor(style["axes.facecolor"])
                    axis.pane.set_edgecolor(style["axes.edgecolor"])
                except Exception:
                    pass
    # Recolor any existing text artists (suptitle etc.)
    for t in getattr(fig, "texts", []):
        try:
            t.set_color(style["text.color"])
        except Exception:
            pass
