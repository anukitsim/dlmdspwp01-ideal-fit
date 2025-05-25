#!/usr/bin/env python3
"""
src/main.py
============

Entry-point for the Ideal-Fit pipeline:
  - load:   ingest data/training_data.csv & data/ideal_functions.csv into the SQLite DB (wiping any old copy)
  - run:    select best ideals, map data/test_data.csv points
  - viz:    build & save the Bokeh HTML plot
  - all:    do load → run → viz in one go
"""

import argparse
import sys
import os
from pathlib import Path

from .database import DatabaseManager
from .loader import TrainingLoader, IdealLoader, TestLoader
from .selector import select_best_ideals
from .mapper import map_test_points
from .visualise import Plotter


def load_data(db_path: str, train_csv: str, ideal_csv: str) -> None:
    """
    Load training and ideal CSV files into the SQLite database.

    This will remove any existing database file at db_path,
    then create tables and insert rows from the given CSVs.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    train_csv : str
        Path to the training_data.csv file.
    ideal_csv : str
        Path to the ideal_functions.csv file.
    """
    # Wipe old database so we don't re-insert identical rows
    if os.path.exists(db_path):
        print(f"→ Removing existing database at {db_path!r}")
        os.remove(db_path)

    db = DatabaseManager(db_path)
    print(f"→ Loading training data from {train_csv!r} into table 'training'")
    TrainingLoader(train_csv).to_db(db.engine)
    print(f"→ Loading ideal functions from {ideal_csv!r} into table 'ideal'")
    IdealLoader(ideal_csv).to_db(db.engine)
    print("✔ load complete.")


def run_matching(db_path: str) -> None:
    """
    Run the matching and mapping steps on the database.

    This will select the best matching ideal functions for each noisy training curve,
    and then map test points to those functions if they fit the tolerance rule.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    """
    db = DatabaseManager(db_path)
    print("→ Selecting best-match ideals …")
    mapping = select_best_ideals(db.engine)
    print(f"✔ chosen ideals: {mapping}")
    print("→ Mapping test points …")
    count = map_test_points(db.engine)
    print(f"✔ mapped {count} test points into 'mapping' table.")


def visualize(outfile: str = "outputs/fit.html") -> None:
    """
    Generate an interactive Bokeh plot and save it as HTML.

    The plot shows the noisy training curves, their chosen ideal curves,
    and the accepted test points with a hover tool for deviations.

    Parameters
    ----------
    outfile : str
        Path where the HTML file will be saved.
    """
    Path("outputs").mkdir(exist_ok=True)
    print(f"→ Generating visualization at {outfile!r}")
    Plotter().save_html(outfile)
    print("✔ wrote", outfile)


def main() -> None:
    """
    Parse command-line arguments and run the selected pipeline step.

    Steps available: load, run, viz, all.
    """
    parser = argparse.ArgumentParser(description="Ideal-Fit matching pipeline")
    parser.add_argument("step",
                        choices=["load", "run", "viz", "all"],
                        help="Which part to execute")
    parser.add_argument("--db",    default="db/idealfit.db",
                        help="SQLite file path")
    parser.add_argument("--train", default="data/training_data.csv",
                        help="Training CSV path (e.g. data/training_data.csv)")
    parser.add_argument("--ideal", default="data/ideal_functions.csv",
                        help="Ideal functions CSV (e.g. data/ideal_functions.csv)")
    parser.add_argument("--test",  default="data/test_data.csv",
                        help="Test-points CSV (e.g. data/test_data.csv)")

    args = parser.parse_args()

    if args.step in ("load", "all"):
        load_data(args.db, args.train, args.ideal)

    if args.step in ("run", "all"):
        run_matching(args.db)

    if args.step in ("viz", "all"):
        visualize()

    if args.step == "all":
        print("Pipeline complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()