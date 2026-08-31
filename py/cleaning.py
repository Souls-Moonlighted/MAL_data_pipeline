import marimo

__generated_with = "0.24.0"
app = marimo.App(width="columns")

with app.setup:
    import marimo as mo
    import numpy as np
    import scipy.stats as stats
    import polars as pl
    import polars.selectors as cs
    import seaborn as sns
    import matplotlib.pyplot as plt
    from collections.abc import Collection
    import logging


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Pre processing phase
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Checking the dataset
    """)
    return


@app.cell
def _():
    pl.scan_csv("./dataset/anime_entries.csv").collect_schema().names()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Remove unnecessary columns and load dataset
    """)
    return


@app.cell
def _():
    raw_df = (
        pl.scan_csv(
            "./dataset/anime_entries.csv", try_parse_dates=True
        )  # We use scan_csv instead of read_csv to optimize ram usage, it help remove unnecessary columns before load it into memory
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
        .collect()
    )
    return (raw_df,)


@app.cell
def _(raw_df):
    raw_df
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Data types in raw dataset
    """)
    return


@app.cell
def _(raw_df):
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
def _(pre_col_types, raw_df):
    plt.pie(
        pre_col_types.to_pandas()["count"],
        labels=pre_col_types.to_pandas()["data_type"],
        autopct="%1.2f%%",  # This format equivalent to xx.xx%
    )
    plt.title("Percentage of data types in the dataframe")
    plt.legend(pre_col_types.to_pandas()["data_type"])
    plt.tight_layout()
    plt.text(0.5, -1.25, f"Total columns: {len(raw_df.columns)}")
    plt.show()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Unique values of each column
    """)
    return


@app.cell
def _(raw_df):
    nunique_df = raw_df.select(pl.all().n_unique())
    nunique_df
    return (nunique_df,)


@app.cell
def _(nunique_df):
    _unique_plot = sns.barplot(data=nunique_df.to_pandas(), orient="h")
    _unique_plot.set_ylabel("Columns")
    _unique_plot.set_xlabel("Unique count")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Caculate missing values
    """)
    return


@app.cell
def _(raw_df):
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
def _(pre_clean_miss_val_count):
    _mis_val_plot = sns.barplot(
        data=pre_clean_miss_val_count.to_pandas(), orient="h"
    )
    _mis_val_plot.set_xlabel("Null count")
    _mis_val_plot.set_ylabel("Columns")
    return


@app.cell
def _(pre_clean_miss_val_pct):
    _mis_pct_plot = sns.barplot(
        data=pre_clean_miss_val_pct.to_pandas(), orient="h"
    )
    _mis_pct_plot.set_xlabel("Null percentage")
    _mis_pct_plot.set_ylabel("Columns")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    This is actually meaningless because they are all divided by the same number, so the two plots are not different at all.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Processing phase
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(f"""
    Before processing we need some conventions and notes:

    1. We use None value to represent data missing or unidentified value

    2. Final dataframe created after processing phase not grantee same amount of columns (usually more), columns datatype and columns name
    3. If a variable have an under prefix (_ prefix), marimo make it only visible in its cell. That mean you can not (and should not if you using jupyter/colab) use it outside
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Let's take a sample from raw dataframe
    """)
    return


@app.cell
def _(raw_df):
    raw_df.select(pl.all().sample(30, seed=10))
    return


@app.cell
def _():
    # A list containing polars expressions, which will be used later to create the final data frame
    exprs: list[pl.Expr] = []
    return (exprs,)


@app.cell(hide_code=True)
def _():
    mo.md(f"""
    We will convert the columns have few unique values to enum type

    Considering string format there are 6 columns meet requirements to become enum : type, status, source, demographic, age_rating, season

    But first we need clean them
    """)
    return


@app.cell
def _():
    enum_cols = [
        "type",
        "status",
        "source",
        "demographic",
        "age_rating",
        "season",
    ]
    return (enum_cols,)


@app.function
# A function used to generate polar expressions, in which the incorrect value is converted to the correct value.
# An inaccurate value is a value that is essentially null but appears in a different form (placeholder value/magic number/encoded value)
def error_val_trans(
    col: str,
    old_val: Collection[str | int | float] | str | int | float,
    new_val: str | int | float | None,
) -> pl.Expr:
    match old_val:
        case str() | int() | float():
            return pl.col(col).replace(old_val, new_val)
        case _:
            return (
                pl.when(pl.col(col).is_in(old_val))
                .then(new_val)
                .otherwise(pl.col(col))
                .alias(col)
            )


@app.cell
def _(enum_cols, nunique_df):
    nunique_df.select(enum_cols)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    251 is too large to manually investigate all values, luckily premier column have good string format we can use regex to identify error value
    """)
    return


@app.cell
def _(raw_df):
    raw_df.filter(
        ~pl.col("season").str.contains(r"^(Spring|Summer|Fall|Winter)\s\d{4}$")
    ).select(pl.col("season")).unique()
    return


@app.cell
def _(enum_cols, raw_df):
    with pl.Config(
        tbl_rows=17
    ):  # Set maxium printable row of a dataframe to 17
        for _col in enum_cols[0:-1]:  # Exclude premier column
            print(raw_df.select(pl.col(_col).unique().drop_nulls()))
    return


@app.cell
def _(enum_cols, exprs: list[pl.Expr], raw_df):
    for _col in enum_cols:
        cal = pl.Enum(raw_df.select(pl.col(_col).unique().drop_nulls()))
        exprs.append(error_val_trans(_col, ["Unknown", "?"], None).cast(cal))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Convert columns with the similar string format to list[str] datatype
    """)
    return


@app.cell
def _(exprs: list[pl.Expr]):
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
    for _col in lst_cast_cols:
        exprs.append(lst_cast(_col))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    There is a column with an incorrect data type: episodes. This column must be of numeric type.
    """)
    return


@app.cell
def _(exprs: list[pl.Expr]):
    # 16-bit unsigned interger is large enough to store this columns value.
    exprs.append(
        pl.col("episodes").cast(pl.UInt16, strict=False)
    )  # Non numeric values are removed.
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Now come to the hard part, time-series processing
    """)
    return


@app.cell
def _(raw_df):
    raw_df.filter(
        ~pl.col("broadcast_time").str.contains(
            r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)s at ([01]\d|2[0-3]):([0-5]\d) \(([A-Z]{2,5})\)$"
        )
    ).select(pl.col("broadcast_time")).unique()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    This is an unexpected result. Each side has its own unique placeholder value, so let's split it.
    """)
    return


@app.cell
def _(exprs: list[pl.Expr]):
    exprs.append(
        pl.col("broadcast_time")
        .str.split_exact(by=" at ", n=1)
        .struct.rename_fields(["broadcast_day", "broadcast_hours"])
    )
    return


@app.cell(hide_code=True)
def _():
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
def _():
    mo.md(r"""
    And a list of other expressions to remove error values from the split columns.
    """)
    return


@app.cell
def _():
    nested_err_remove: list[pl.Expr] = []
    return (nested_err_remove,)


@app.cell
def _(nested_err_remove: list[pl.Expr]):
    for _col in ["broadcast_day", "broadcast_hours"]:
        nested_err_remove.append(error_val_trans(_col, "Unknown", None))
    return


@app.cell
def _(raw_df):
    raw_df.select(pl.col("airing_date")).sample(n=30, seed=5)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Since anime comes in various formats (movies, TV series, OVAs, ONAs, etc.), there is no universal format for air dates. Therefore, I split the data into two columns representing the start and end dates while keeping them as strings, allowing us to use regex later to extract the information we need.
    """)
    return


@app.cell
def _(exprs: list[pl.Expr], nested_cols: list[str]):
    exprs.append(
        pl.col("airing_date")
        .str.split_exact(" to ", n=1)
        .struct.rename_fields(["first_air_date", "last_air_date"])
    )
    nested_cols.append("airing_date")
    return


@app.cell
def _(nested_err_remove: list[pl.Expr]):
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
    exprs: list[pl.Expr],
    nested_cols: list[str],
    nested_err_remove: list[pl.Expr],
    raw_df,
):
    final_df = (
        raw_df.with_columns(exprs)
        .unnest(nested_cols)
        .with_columns(nested_err_remove)
    )
    return (final_df,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Post processing phase
    """)
    return


@app.cell
def _(final_df):
    final_df
    return


@app.cell
def _(final_df, raw_df):
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
    return (
        cols_with_nulls_final,
        post_clean_miss_val_count,
        post_clean_miss_val_pct,
    )


@app.cell
def _(cols_with_nulls, cols_with_nulls_final, final_df, raw_df):
    print(f"Additional column: {len(final_df.columns) - len(raw_df.columns)}")
    print(len(cols_with_nulls_final) - len(cols_with_nulls))
    return


@app.cell
def _(final_df):
    post_col_list = [col for col in final_df.schema]
    post_col_types = (
        (
            pl.DataFrame(
                {
                    "column": post_col_list,
                    "data_type": [
                        type
                        for type in [
                            str(final_df.schema[col]) for col in post_col_list
                        ]
                    ],
                }
            )
        )
        .with_columns(
            pl.when(pl.col("data_type").str.contains("Enum"))
            .then(pl.lit("Enum"))
            .otherwise(pl.col("data_type"))
            .alias("data_type")
        )
        .group_by("data_type")
        .all()
        .with_columns(pl.col("column").list.len().alias("count"))
    )
    post_col_types
    return (post_col_types,)


@app.cell
def _(final_df, post_col_types):
    plt.pie(
        post_col_types.to_pandas()["count"],
        labels=post_col_types.to_pandas()["data_type"],
        autopct="%1.2f%%",  # This format equivalent to xx.xx%
    )
    plt.title("Percentage of data types in the dataframe")
    plt.legend(post_col_types.to_pandas()["data_type"], loc=(1, 0.6))
    plt.tight_layout()
    plt.text(0.9, -1.25, f"Total columns: {len(final_df.columns)}")
    plt.show()
    return


@app.cell
def _(post_clean_miss_val_count):
    _mis_val_plot = sns.barplot(
        data=post_clean_miss_val_count.to_pandas(), orient="h"
    )
    _mis_val_plot.set_xlabel("Null count")
    _mis_val_plot.set_ylabel("Columns")
    return


@app.cell
def _(post_clean_miss_val_pct):
    _mis_pct_plot = sns.barplot(
        data=post_clean_miss_val_pct.to_pandas(), orient="h"
    )
    _mis_pct_plot.set_xlabel("Null percentage")
    _mis_pct_plot.set_ylabel("Columns")
    return


if __name__ == "__main__":
    app.run()
