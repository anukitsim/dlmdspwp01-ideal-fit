"""
src/main.py

Entry-point for the Ideal-Fit pipeline:
  - load:   ingest train + ideal CSVs into the SQLite DB
  - run:    select best ideals, map test points
  - viz:    build & save the Bokeh HTML plot
  - all:    do load → run → viz in one go
"""

import argparse
import sys
from pathlib import Path

from .database import DatabaseManager
from .loader import TrainingLoader, IdealLoader, TestLoader
from .selector import select_best_ideals
from .mapper import map_test_points
from .visualise import Plotter


def load_data(db_path: str, train_csv: str, ideal_csv: str):
    db = DatabaseManager(db_path)
    print(f"→ Loading training data from {train_csv!r} into table 'training'")
    TrainingLoader(train_csv).to_db(db.engine)
    print(f"→ Loading ideal functions from {ideal_csv!r} into table 'ideal'")
    IdealLoader(ideal_csv).to_db(db.engine)
    print("✔ load complete.")


def run_matching(db_path: str):
    db = DatabaseManager(db_path)
    print("→ Selecting best-match ideals …")
    mapping = select_best_ideals(db.engine)
    print(f"✔ chosen ideals: {mapping}")
    print("→ Mapping test points …")
    count = map_test_points(db.engine, TestLoader, mapping)
    print(f"✔ mapped {count} test points into ‘mapping’ table.")


def visualize(outfile: str = "outputs/fit.html"):
    Path("outputs").mkdir(exist_ok=True)
    print(f"→ Generating visualization at {outfile!r}")
    Plotter().save_html(outfile)


def main():
    parser = argparse.ArgumentParser(description="Ideal-Fit matching pipeline")
    parser.add_argument("step",
                        choices=["load","run","viz","all"],
                        help="Which part to execute")
    parser.add_argument("--db",    default="db/idealfit.db",
                        help="SQLite file path")
    parser.add_argument("--train", default="data/train.csv",
                        help="Training CSV path")
    parser.add_argument("--ideal", default="data/ideal.csv",
                        help="Ideal functions CSV")
    parser.add_argument("--test",  default="data/test.csv",
                        help="Test-points CSV")

    args = parser.parse_args()

    if args.step in ("load","all"):
        load_data(args.db, args.train, args.ideal)

    if args.step in ("run","all"):
        run_matching(args.db)

    if args.step in ("viz","all"):
        visualize()

    if args.step == "all":
        print("Pipeline complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
