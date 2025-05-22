"""
visualise.py 
--------------

- draws the four noisy training curves
- overlays their four chosen ideal curves
- drops the accepted test points, coloured by which ideal they matched
- hover tooltip shows  |y_test - y_ideal|  (= deviation)

The script writes an interactive HTML file to  outputs/fit.html
Can be run once from the project root:

    python src/visualise.py
"""

from pathlib import Path
from typing import List

import pandas as pd
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category10
from bokeh.plotting import figure

from .database import DatabaseManager


def _load_all(db: DatabaseManager):
    """Pull every table we need as pandas frames."""
    training = pd.read_sql("SELECT * FROM training", db.engine)
    ideal = pd.read_sql("SELECT * FROM ideal", db.engine)
    chosen = pd.read_sql("SELECT * FROM chosen_ideals", db.engine)
    mapping = pd.read_sql("SELECT * FROM mapping", db.engine)
    return training, ideal, chosen, mapping


class Plotter:
    """Little helper that draws and saves the interactive HTML file."""

    def __init__(self, db_path: str = "db/idealfit.db") -> None:
        self.db = DatabaseManager(db_path)

        # load everything once
        (
            self.training_df,
            self.ideal_df,
            self.chosen_df,
            self.map_df,
        ) = _load_all(self.db)

        # make sure outputs/ exists
        Path("outputs").mkdir(exist_ok=True)

    # --------------------------------------------------
    def build_figure(self):
        """Create a Bokeh Figure with curves and points."""
        p = figure(
            title="Ideal-Fit results",
            width=900,
            height=500,
            x_axis_label="x",
            y_axis_label="y",
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )

        colours: List[str] = list(Category10[10])

        # --- training + ideal curves ------------------
        for idx, row in self.chosen_df.iterrows():
            tcol = row["training_col"]
            icol = row["ideal_col"]
            colour = colours[idx]

            p.line(
                self.training_df["x"],
                self.training_df[tcol],
                legend_label=f"{tcol} (noisy)",
                line_color=colour,
                line_dash="dashed",
                line_width=1.5,
            )

            p.line(
                self.ideal_df["x"],
                self.ideal_df[icol],
                legend_label=f"{icol} (clean)",
                line_color=colour,
                line_width=2,
            )

        # --- accepted test points ---------------------
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

    # --------------------------------------------------
    def save_html(self, outfile: str = "outputs/fit.html") -> None:
        """Generate the plot and write the HTML file."""
        output_file(outfile, title="Ideal-Fit visualisation")
        save(self.build_figure())
        print(f"✔ wrote {outfile}")


if __name__ == "__main__":
    Plotter().save_html()
