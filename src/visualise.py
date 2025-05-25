"""
src/visualise.py
----------------

Draws the four noisy training curves and their matched ideal curves,
then overlays accepted test points, colored by their assigned ideal.
Hover tool shows deviation |y_test - y_ideal|.

Writes an interactive HTML file to outputs/fit.html.
Run from project root with:
    python -m src.visualise
"""

from pathlib import Path
from typing import List, Tuple

import pandas as pd
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category10
from bokeh.plotting import figure

from .database import DatabaseManager


def _load_all(db: DatabaseManager) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all required tables into pandas DataFrames.

    Parameters
    ----------
    db : DatabaseManager
        Database manager connected to the SQLite file.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        DataFrames for training, ideal, chosen_ideals, and mapping.
    """
    training = pd.read_sql("SELECT * FROM training", db.engine)
    ideal = pd.read_sql("SELECT * FROM ideal", db.engine)
    chosen = pd.read_sql("SELECT * FROM chosen_ideals", db.engine)
    mapping = pd.read_sql("SELECT * FROM mapping", db.engine)
    return training, ideal, chosen, mapping


class Plotter:
    """
    Helper to build and save a Bokeh plot of the matching results.

    Attributes
    ----------
    training_df : pd.DataFrame
        Noisy training curves.
    ideal_df : pd.DataFrame
        All ideal reference curves.
    chosen_df : pd.DataFrame
        Chosen ideal for each training curve.
    map_df : pd.DataFrame
        Accepted test points with their assignments and deviations.
    """

    def __init__(self, db_path: str = "db/idealfit.db") -> None:
        """
        Initialize Plotter and load data.

        Parameters
        ----------
        db_path : str, optional
            Path to the SQLite database file (default "db/idealfit.db").
        """
        self.db = DatabaseManager(db_path)
        self.training_df, self.ideal_df, self.chosen_df, self.map_df = _load_all(self.db)
        # Ensure output folder exists
        Path("outputs").mkdir(exist_ok=True)

    def build_figure(self):
        """
        Create a Bokeh Figure with:
          - Dashed lines for noisy training curves
          - Solid lines for chosen ideal curves
          - Black dots for accepted test points

        Returns
        -------
        bokeh.plotting.figure.Figure
            The configured Bokeh figure object.
        """
        p = figure(
            title="Ideal-Fit results",
            width=900,
            height=500,
            x_axis_label="x",
            y_axis_label="y",
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )
        colors: List[str] = list(Category10[10])

        # Plot training and ideal curves
        for idx, row in self.chosen_df.iterrows():
            tcol = row["training_col"]
            icol = row["ideal_col"]
            color = colors[idx]

            p.line(
                self.training_df["x"],
                self.training_df[tcol],
                legend_label=f"{tcol} (noisy)",
                line_color=color,
                line_dash="dashed",
                line_width=1.5,
            )
            p.line(
                self.ideal_df["x"],
                self.ideal_df[icol],
                legend_label=f"{icol} (clean)",
                line_color=color,
                line_width=2,
            )

        # Plot accepted test points
        cds = ColumnDataSource(self.map_df)
        p.circle(
            "x",
            "y",
            size=6,
            source=cds,
            color="black",
            fill_alpha=0.7,
            legend_label="Accepted test points",
        )

        # Add hover tool for deviation
        hover = HoverTool(
            tooltips=[
                ("x", "@x"),
                ("y", "@y"),
                ("ideal", "@ideal_id"),
                ("deviation", "@deviation{0.000}"),
            ]
        )
        p.add_tools(hover)
        p.legend.click_policy = "hide"

        return p

    def save_html(self, outfile: str = "outputs/fit.html") -> None:
        """
        Generate the Bokeh plot and save it as an HTML file.

        Parameters
        ----------
        outfile : str, optional
            Path to the output HTML file (default "outputs/fit.html").
        """
        output_file(outfile, title="Ideal-Fit visualization")
        save(self.build_figure())
        print(f"✔ wrote {outfile}")


if __name__ == "__main__":
    Plotter().save_html()
