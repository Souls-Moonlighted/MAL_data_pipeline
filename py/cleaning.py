import marimo

__generated_with = "0.23.14"
app = marimo.App(width="columns")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import scipy
    import polars as pl
    import polars.selectors as cs
    import seaborn as sns
    import pyarrow

    return mo, pl, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A brief overview of raw dataset
    """)
    return


@app.cell
def _(pl):
    pl.read_csv("./dataset/anime_entries.csv").columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Remove unnecessary columns
    """)
    return


@app.cell
def _(pl):
    raw_df = (
        pl.read_csv("./dataset/anime_entries.csv", try_parse_dates=True)
        .drop(
            # Drop unnecessary columns
            pl.col(
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
        )
        .rename(
            {
                "item_type": "type",
                "premier_date": "premier",
                "broadcast_date": "broadcast_time",
            }
        )
    )
    return (raw_df,)


@app.cell
def _(raw_df):
    raw_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Data types in raw dataset
    """)
    return


@app.cell
def _(pl, raw_df):
    col_list = [col for col in raw_df.schema]
    pre_col_types = (
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
    pre_col_types
    return (pre_col_types,)


@app.cell
def _(pre_col_types, sns):
    sns.barplot(data=pre_col_types.to_pandas(), x="data_type", y="count")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Unique values of each column
    """)
    return


@app.cell
def _(pl, raw_df):
    nunique_df = raw_df.select(pl.all().n_unique())
    nunique_df
    return (nunique_df,)


@app.cell
def _(nunique_df, sns):
    _unique_plot = sns.barplot(data=nunique_df.to_pandas(), orient="h")
    _unique_plot.set_ylabel("Columns")
    _unique_plot.set_xlabel("Unique count")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Caculate missing values
    """)
    return


@app.cell
def _(pl, raw_df):
    cols_with_nulls = [
        col for col in raw_df.columns if raw_df[col].null_count() > 0
    ]
    print(f"Missing value columns:\n {cols_with_nulls}")
    pre_clean_miss_val_count = raw_df.select(
        pl.col(cols_with_nulls).null_count()
    )
    print(f"Mising values count:\n {pre_clean_miss_val_count}")
    pre_clean_miss_val_pct = pre_clean_miss_val_count.with_columns(
        (pl.all() / len(raw_df) * 100).round(2)
    )
    print(f"Missing values percentage: \n {pre_clean_miss_val_pct}")
    return cols_with_nulls, pre_clean_miss_val_count, pre_clean_miss_val_pct


@app.cell
def _(pre_clean_miss_val_count, pre_clean_miss_val_pct, sns):
    _mis_val_plot = sns.barplot(
        data=pre_clean_miss_val_count.to_pandas(), orient="h"
    )
    _mis_val_plot.set_xlabel("Null values")
    _mis_val_plot.set_ylabel("Columns")
    _mis_pct_plot = sns.barplot(
        data=pre_clean_miss_val_pct.to_pandas(), orient="h"
    )
    _mis_pct_plot.set_xlabel("Null per")
    _mis_pct_plot.set_ylabel("Columns")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Processing phase
    """)
    return


@app.cell
def _(pl, raw_df):
    raw_df.select(pl.all().sample(30, seed=10))
    return


@app.cell
def _(pl):
    # A list containing polars expressions, which will be used later to create the final data frame
    exprs: list[pl.Expr] = []
    return (exprs,)


@app.cell
def _(pl):
    # A function used to generate polar expressions, in which the incorrect value is converted to the correct value.
    # An inaccurate value is a value that is essentially null but appears in a different form (placeholder value/magic number/encoded value)
    def error_val_trans(col: str, old_val: any, new_val: any):
        return pl.col(col).replace(old_val, new_val)

    return (error_val_trans,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start with the columns that have few unique values and can be converted to enum variables.
    """)
    return


@app.cell
def _(nunique_df, raw_df):
    cal_cols = raw_df.select(
        [
            col
            for col, val in zip(nunique_df.columns, nunique_df.row(0))
            # The number 20 is actually some kind of personal preference, it not some mathematical number or something else 
            # and it is bigger than 17 and small than 251 ^_^
            # You can treat   this number as a magic number
            # This is my day of birth by the way
            if val <= 20
        ]
    ).columns
    return (cal_cols,)


@app.cell
def _(cal_cols, pl, raw_df):
    with pl.Config(tbl_rows=20):
        for _ in cal_cols:
            print(raw_df.select(pl.col(_).unique().drop_nulls()))
    return


@app.cell
def _(cal_cols, error_val_trans, exprs: "list[pl.Expr]", pl, raw_df):
    # Be careful with this code, it actually leads to some bugs if it runs multiple times.
    for _ in cal_cols:
        cal = pl.Enum(raw_df.select(pl.col(_).unique().drop_nulls()))
        exprs.append(error_val_trans(_, "Unknown", None).cast(cal))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Convert columns with the same string format to list[str] datatype
    """)
    return


@app.cell
def _(exprs: "list[pl.Expr]", pl):
    # List of columns that have similar string formats.
    lst_cast_cols = ["producers", "licensors", "studios", "genres", "themes"]

    # A function to cast str to list[str]
    def lst_cast(col: str):
        return (
            # The symbol [] represents the null value, so we'll convert it to null before proceeding to the next step
            pl.when(pl.col(col) == "[]")
            .then(None)
            .otherwise(
                pl.col(col)
                .str.strip_prefix('["')
                .str.strip_suffix('"]')
                .str.split('", "')
            )
            .alias(col)
        )

    # Just like the code above, this code will also cause an error if you run it multiple times, so be careful.
    for _ in lst_cast_cols:
        exprs.append(lst_cast(_))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There is a column with an incorrect data type: episodes. This column must be of numeric type.
    """)
    return


@app.cell
def _(exprs: "list[pl.Expr]", pl):
    # 16-bit unsigned interger is enough.
    exprs.append(
        pl.col("episodes").cast(pl.UInt16, strict=False)
    )  # Non numeric values are removed.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now come to the hard part, time-series processing
    """)
    return


@app.cell
def _(pl, raw_df):
    raw_df.filter(
        ~pl.col("premier").str.contains(
            r"^(Spring|Summer|Fall|Winter)\s\d{4}$"
        )
    ).select(pl.col("premier")).unique()
    return


@app.cell
def _(error_val_trans, exprs: "list[pl.Expr]"):
    exprs.append(error_val_trans("premier", "?", None))
    return


@app.cell
def _(pl, raw_df):
    raw_df.filter(
        ~pl.col("broadcast_time").str.contains(
            r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)s at ([01]\d|2[0-3]):([0-5]\d) \(([A-Z]{2,5})\)$"
        )
    ).select(pl.col("broadcast_time")).unique()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is an unexpected result (for me), splitting this column into two can solve this problem
    """)
    return


@app.cell
def _(exprs: "list[pl.Expr]", pl):
    exprs.append(
        pl.col("broadcast_time")
        .str.split_exact(by=" at ", n=1)
        .struct.rename_fields(["broadcast_day", "broadcast_hours"])
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We need to call the "unnest" method to split this column into 2 separate columns but we cannot do this within the "with_columns" method (actually we can but it doesn't give us the desired result) so we need to create a list of columns to store information about which columns are nested.
    """)
    return


@app.cell
def _():
    nested_cols: list[str] = []
    return (nested_cols,)


@app.cell
def _(nested_cols: list[str]):
    nested_cols.append("broadcast_time")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And a list of other expressions to remove error values from the split columns.
    """)
    return


@app.cell
def _(pl):
    nested_err_remove: list[pl.Expr] = []
    return (nested_err_remove,)


@app.cell
def _(nested_err_remove: "list[pl.Expr]", pl):
    for col in ["broadcast_day", "broadcast_hours"]:
        nested_err_remove.append(
            pl.when(
                pl.col(col).is_in(["Unknown", "Not scheduled once per week"])
            )
            .then(None)
            .otherwise(pl.col(col))
            .alias(col)
        )
    return


@app.cell
def _(pl, raw_df):
    raw_df.select(pl.col("airing_date")).sample(n=20, seed=5)
    return


@app.cell
def _():
    return


@app.cell
def _(exprs: "list[pl.Expr]", nested_cols: list[str], pl):
    exprs.append(
        pl.col("airing_date")
        .str.split_exact(" to ", n=1)
        .struct.rename_fields(["first_air_date", "last_air_date"])
    )
    nested_cols.append("airing_date")
    return


@app.cell
def _(nested_err_remove: "list[pl.Expr]", pl):
    for _col in ["first_air_date", "last_air_date"]:
        nested_err_remove.append(
            pl.when(pl.col(_col).is_in(["?", "Not available"]))
            .then(None)
            .otherwise(pl.col(_col))
            .alias(_col)
        )
    return


@app.cell
def _(
    exprs: "list[pl.Expr]",
    nested_cols: list[str],
    nested_err_remove: "list[pl.Expr]",
    raw_df,
):
    final_df = (
        raw_df.with_columns(exprs)
        .unnest(nested_cols)
        .with_columns(nested_err_remove)
    )
    return (final_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## After processing data frame
    """)
    return


@app.cell
def _(final_df):
    final_df
    return


@app.cell
def _(final_df, pl, raw_df):
    cols_with_nulls_final = [
        col for col in final_df.columns if final_df[col].null_count() > 0
    ]
    print(f"Missing value columns:\n {cols_with_nulls_final}")
    post_clean_miss_val_count = final_df.select(
        pl.col(cols_with_nulls_final).null_count()
    )
    print(f"Mising values count:\n {post_clean_miss_val_count}")
    post_clean_miss_val_pct = post_clean_miss_val_count.with_columns(
        (pl.all() / len(raw_df) * 100).round(2)
    )
    print(f"Missing values percentage: \n {post_clean_miss_val_pct}")
    return (cols_with_nulls_final,)


@app.cell
def _(cols_with_nulls, cols_with_nulls_final, final_df, raw_df):
    print(f"Additional column: {len(final_df.columns) - len(raw_df.columns)}")
    print(len(cols_with_nulls_final) - len(cols_with_nulls))
    return


@app.cell
def _(final_df, pl):
    test = (final_df.select(pl.col("studios")).explode(
        pl.col("studios"),empty_as_null=True
    ).drop_nulls()).to_series().value_counts()
    return (test,)


@app.cell
def _(pl, test):
    test.sort(pl.col("count"),descending=True)
    return


@app.cell
def _(sns, test):
    sns.kdeplot(data=test["count"])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
