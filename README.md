# Ideal-Fit — DLMDSPWP01 *Programming with Python*

> **Goal** Match four noisy training functions to 50 ideal functions via least-squares;  
> classify new test points if │y_test − y_ideal│ ≤ √2·(max deviation).

* Python 3.10 • Pandas • NumPy • SQLAlchemy • Bokeh  
* SQLite tables: `training`, `ideal`, `chosen_ideals`, `mapping`  
* Unit-tested with **pytest**; fully modular OOP design per IU brief.

## How to run

```bash
# 1) build DB & choose ideal curves
python src/main.py

# 2) render interactive plot → outputs/fit.html
python -m src.visualise

# 3) run all automated tests (expect “5 passed”)
pytest -q

