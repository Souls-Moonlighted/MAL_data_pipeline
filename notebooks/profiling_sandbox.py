import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import math
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import polars as pl
    import seaborn as sns
    from scipy import stats


@app.cell
def _():
    dir = Path("../dataset/anime_entries.csv")
    if dir.exists():
        pass
    else:
        mo.stop(predicate=True,output="Directory does not exist; stopping notebook cell.")
    return (dir,)


@app.cell
def _(dir):
    raw_df = (
        pl.read_csv(dir, try_parse_dates=True)
        .drop(
            [
                "link",
                "synonymns",
                "japanese_name",
                "english_name",
                "german_name",
                "french_name",
                "spanish_name",
                "description",
                "background",
            ]
        )
        .rename(
            {
                "item_type": "type",
                "premier_date": "season",
                "broadcast_date": "broadcast_time",
            }
        )
    )
    return (raw_df,)


@app.function
def compute_sample_size(
    population_size: int,
    confidence_level: float = 0.95,
    margin_of_error: float = 0.05,
    proportion: float = 0.5,
) -> int:

    alpha = 1.0 - confidence_level
    z_score = stats.norm.ppf(1.0 - alpha / 2.0)

    variance = proportion * (1.0 - proportion)
    n_0 = (z_score**2 * variance) / (margin_of_error**2)

    if population_size > 0:
        n = n_0 / (1.0 + (n_0 - 1.0) / population_size)
    else:
        n = n_0

    return math.ceil(n)


@app.cell
def _(raw_df):
    sample_size = compute_sample_size(raw_df.height)
    random_seed = 0
    return random_seed, sample_size


@app.cell
def _(random_seed, raw_df, sample_size):
    raw_df.sample(sample_size, seed=random_seed)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    A quick look at this sample dataframe reveals several anomalies:
    - The `episodes` column has a string data type instead of a numeric one.
    - `Unknown` and `?` values appear in multiple string-type columns
    - `licensors`, `studios` and `themes` have `[]` value (suggesting an error or empty value) and these columns datatype missmatch (list[str] not str)
    - Time series column `airing_date` does not follow any standard format
    """)
    return


@app.cell
def _(raw_df):
    col_list = [col for col in raw_df.schema]
    col_types = (
        pl.DataFrame(
            {
                "column": col_list,
                "data_type": [
                    type for type in [raw_df.schema[col] for col in col_list]
                ],
            }
        )
        .group_by(pl.col("data_type"))
        .all()
    ).with_columns(pl.col("column").list.len().alias("count"))
    col_types
    return (col_types,)


@app.cell
def _(col_types, raw_df):
    plt.pie(
        col_types.to_pandas()["count"],
        labels=col_types.to_pandas()["data_type"],
        autopct="%1.2f%%",  # This format equivalent to xx.xx%
    )
    plt.title("Percentage of data types in the dataframe")
    plt.legend(col_types.to_pandas()["data_type"])
    plt.tight_layout()
    plt.text(0.5, -1.25, f"Total columns: {len(raw_df.columns)}")
    plt.show()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    String-type columns type dominate the dataframe.
    """)
    return


@app.cell
def _(raw_df):
    nunique_df = raw_df.select(pl.all().n_unique())
    _unique_plot = sns.barplot(data=nunique_df.to_pandas(), orient="h")
    _unique_plot.set_ylabel("Columns")
    _unique_plot.set_xlabel("Unique count")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Columns with a low number of unique values ​​could be converted to the enum type, but further investigation is required to determine this.
    """)
    return


@app.cell
def _(raw_df):
    cols_with_nulls = [col for col in raw_df.columns if raw_df[col].null_count() > 0]
    null_val_count = raw_df.select(pl.col(cols_with_nulls).null_count())
    _null_pct_plot = sns.barplot(
        data=(null_val_count * 100 / raw_df.height).to_pandas(), orient="h"
    )
    _null_pct_plot.set_xlabel("Null percentage")
    _null_pct_plot.set_ylabel("Columns")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    `season`, `broadcast_time` and `demographic` contain a lot of null value than any other column, maybe there is some reason behind this
    """)
    return


@app.cell
def _(raw_df):
    raw_df.filter(~raw_df.get_column("episodes").map_elements(str.isnumeric)).select(
        "episodes"
    ).unique()
    return


@app.cell
def _(raw_df):
    raw_df.filter(pl.col("episodes") == "Unknown")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    All records have the value `Unknown` in the `episodes` column for various reasons, none of which hold special significance
    """)
    return


@app.function
def regex_filter(df: pl.DataFrame, col: str, regex: str) -> list[str]:
    return (
        df.filter(~pl.col(col).str.contains(regex))
        .get_column(col)
        .unique()
        .drop_nulls()
        .to_list()
    )


@app.cell
def _(raw_df):
    season_regex = r"^(Spring|Summer|Fall|Winter)\s\d{4}$"
    regex_filter(raw_df, "season", season_regex)
    return


@app.cell
def _(raw_df):
    raw_df.filter(pl.col("season") == "?")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    It appears that these titles lack comprehensive information and data regarding their broadcast seasons, primarily (just primary not all) because they are not widely recognized as "actual" anime. This presents a significant issue: while the project aims to provide information on anime, the majority of people view these works merely as standard animated productions rather than anime. In a sense, these "anime" titles prompt us to question whether the current dataset is good enough, or if the definition of "anime" used within it differs from the public's perception (including me).
    """)
    return


@app.cell
def _(raw_df):
    broadcast_time_regex = r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)s at ([01]\d|2[0-3]):([0-5]\d) \(([A-Z]{2,5})\)$"
    regex_filter(raw_df, "broadcast_time", broadcast_time_regex)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    `Unknown` day value and `Unknown` time in the same column, I need to split this column later
    """)
    return


@app.cell
def _(random_seed, raw_df, sample_size):
    raw_df.sample(sample_size, seed=random_seed).select("airing_date")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Although this column has a non-standard string format, we can still see that by using the split_exact method to split this column into two using the word `to` as the delimiter, we can extract proper information
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    There are also other anomalies, such as rows in the `score`/`ranked` column containing `null` values, and anime titles that have received no ratings (where the value for the number of raters - `score_by` is `zero`). However, the available information is sufficient for processing the dataset.
    """)
    return


if __name__ == "__main__":
    app.run()
