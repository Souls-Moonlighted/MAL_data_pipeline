# MAL Analyse

This project explores a MyAnimeList-style anime dataset and prepares it for analysis with Python. It focuses on cleaning and understanding the raw data, checking missing values, identifying data types, and building a reusable preprocessing workflow for later analysis.

## Project purpose

The repository contains a small data analysis workflow centered on the file `dataset/anime_entries.csv`. The pipeline performs tasks such as:

- loading the dataset lazily with Polars
- removing unnecessary columns
- renaming columns into a cleaner schema
- inspecting data types and counts
- identifying missing values and null ratios
- sampling a manageable subset for exploration
- preparing categorical columns for analysis
- visualizing findings with Seaborn and Matplotlib

The main implementation is in `py/processing.py`, which is built as a Marimo app and can be run interactively.

## Project structure

```text
.
├── dataset/
│   └── anime_entries.csv
├── notebook/
│   └── cleaning.ipynb
├── py/
│   ├── processing.py
│   └── __marimo__/
│       └── session/
│           └── cleaning.py.json
├── pyproject.toml
├── README.md
└── .venv/   # created when dependencies are installed
```

## Tech stack

- Python 3.12+
- Polars for fast dataframe processing
- Pandas for conversion and reporting
- Seaborn and Matplotlib for visualization
- SciPy for statistical utilities
- Marimo for notebook-style interactive analysis

## Setup

Using `uv` is the recommended option because the project already defines dependencies in `pyproject.toml`.

1. Install dependencies:

```bash
uv sync
```

2. Activate the environment if needed:

```bash
source .venv/bin/activate
```

3. Run the analysis app:

```bash
uv run marimo run py/processing.py
```

You can also open the notebook in `notebook/cleaning.ipynb` for a more notebook-oriented workflow.

## Data

The dataset is stored in `dataset/anime_entries.csv` and contains MyAnimeList anime entries. The preprocessing step removes fields such as links, names in other languages, descriptions, and background text to keep the analysis focused on structured metadata.

## Typical workflow

1. Load the CSV with Polars using lazy evaluation.
2. Drop unneeded columns and normalize column names.
3. Inspect schema and missing values.
4. Generate summary visualizations.
5. Sample rows for exploratory analysis.
6. Convert low-cardinality string columns to categorical/enums for analysis.

## Notes

- This repository is intended for exploratory data analysis and preprocessing.
- The dataset is not necessarily cleaned for production use; the pipeline focuses on analysis and understanding.
- The project is a good starting point for extending into deeper anime statistics, genre analysis, or seasonal trends.

## License

No explicit license file is included in the repository, so the project should be used under the default terms of the author unless otherwise specified.
