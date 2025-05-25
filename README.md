# Ideal-Fit — DLMDSPWP01 Programming with Python

> **Goal**: Match four noisy training functions to 50 ideal functions via least-squares; classify new test points if |y\_test − y\_ideal| ≤ √2·(max deviation).

## Features

* Python 3.10
* Pandas, NumPy, SQLAlchemy, Bokeh
* SQLite backend
* Unit-tested with pytest
* Modular object-oriented design

## Installation

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd ideal-fit
   ```
2. **Create a virtual environment & install dependencies**

   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Project Structure

```
ideal-fit/
├── data/
│   ├── train.csv
│   ├── ideal.csv
│   └── test.csv
├── db/
│   └── idealfit.db
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── loader.py
│   ├── selector.py
│   ├── mapper.py
│   └── visualise.py
├── tests/
│   └── test_*.py
├── outputs/
│   └── fit.html
├── requirements.txt
└── README.md
```

## Usage

1. **Load** the CSVs into the database

   ```bash
   python -m src.main load \
     --db db/idealfit.db \
     --train data/train.csv \
     --ideal data/ideal.csv
   ```

2. **Run** the matching & mapping steps

   ```bash
   python -m src.main run \
     --db db/idealfit.db \
     --test data/test.csv
   ```

3. **Visualize** the results

   ```bash
   python -m src.main viz \
     --db db/idealfit.db
   ```

4. **All-in-one** pipeline

   ```bash
   python -m src.main all \
     --db db/idealfit.db \
     --train data/train.csv \
     --ideal data/ideal.csv \
     --test data/test.csv
   ```

## Testing

Run the full test suite:

```bash
pytest -q
```

## Notes

* **Keep** `main.py` in `src/` as the entry-point script for all pipeline steps.
* Ensure `src/` contains `__init__.py` so it is a proper package.
* The SQLite database file (`db/idealfit.db`) will be created on first `load`.

