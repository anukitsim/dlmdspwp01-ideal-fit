# Ideal-Fit — DLMDSPWP01 *Programming with Python*

> **Goal**: Match four noisy training functions to 50 ideal functions via least-squares;  
> classify new test points if │y_test − y_ideal│ ≤ √2·(max deviation).

* Python 3.10 • Pandas • NumPy • SQLAlchemy • Bokeh  
* SQLite tables: `training`, `ideal`, `chosen_ideals`, `mapping`  
* Unit-tested with **pytest**; fully modular OOP design per IU brief.

## How to run

1. **Load** the CSVs into the database  
   ```bash
    python -m src.main load \
      --db db/idealfit.db \
      --train data/train.csv \
      --ideal data/ideal.csv
   
