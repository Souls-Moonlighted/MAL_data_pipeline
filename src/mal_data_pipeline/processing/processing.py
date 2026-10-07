import logging
from pathlib import Path

import polars as pl

from src.processing.pipeline_config import PipelineConfig

logging.basicConfig(
    level=logging.INFO,
    filename=Path("../logs/pipeline.log"),
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)


def apply_schema_normalization(
    lf: pl.LazyFrame, config: PipelineConfig
) -> pl.LazyFrame:

    available_cols = set(lf.collect_schema().names())

    cols_to_drop = [c for c in config.drop_columns if c in available_cols]

    rename_map = {k: v for k, v in config.rename_mapping.items() if k in available_cols}

    return lf.drop(cols_to_drop).rename(rename_map)


def apply_scalar_cleaning(lf: pl.LazyFrame, config: PipelineConfig) -> pl.LazyFrame:

    available_cols = set(lf.collect_schema().names())
    exprs: list[pl.Expr] = []

    for col, (old_val, new_val, target_type) in config.scalar_clean_rules.items():
        if col not in available_cols:
            continue

        expr = pl.when(pl.col(col).is_in(old_val)).then(new_val).otherwise(pl.col(col))

        if target_type is not None:
            expr = expr.cast(target_type, strict=False)
        exprs.append(expr.alias(col))

    return lf.with_columns(exprs) if exprs else lf


def apply_cat_casting(lf: pl.LazyFrame, config: PipelineConfig) -> pl.LazyFrame:

    available_cols = set(lf.collect_schema().names())
    target_cols = [c for c in config.cat_cols if c in available_cols]

    return lf.with_columns(pl.col(target_cols).cast(pl.Categorical))


def apply_str_array_parsing(lf: pl.LazyFrame, config: PipelineConfig) -> pl.LazyFrame:

    available_cols = set(lf.collect_schema().names())
    target_cols = [c for c in config.str_array_columns if c in available_cols]

    if not target_cols:
        return lf

    return lf.with_columns(
        [
            pl.when(pl.col(c).is_in(config.str_array_error_val))
            .then(None)
            .otherwise(pl.col(c).str.extract_all(config.str_array_pattern))
            .alias(c)
            for c in target_cols
        ]
    )


def apply_regex_extractions(lf: pl.LazyFrame, config: PipelineConfig) -> pl.LazyFrame:

    available_cols = set(lf.collect_schema().names())
    struct_cols = []
    exprs = []

    for col, pattern in config.regex_extractions.items():
        if col not in available_cols:
            continue
        struct_col_name = f"__{col}_struct"
        struct_cols.append(struct_col_name)
        exprs.append(pl.col(col).str.extract_groups(pattern).alias(struct_col_name))

    if not exprs:
        return lf

    return (
        lf.with_columns(exprs)
        .unnest(*struct_cols)
        .drop([col for col in config.regex_extractions if col in available_cols])
    )


def inspect_pipe(
    lf: pl.LazyFrame,
    step_name: str,
    sample_size: int,
    show_columns: list[str] | None = None,
) -> pl.LazyFrame:
    if show_columns is None:
        show_columns = lf.collect_schema().names()
    print(f"\n{'=' * 20} [STEP: {step_name}] {'=' * 20}")

    if isinstance(lf, pl.LazyFrame):
        schema = lf.collect_schema()
        print(f"[LazyFrame] Total columns: {len(schema)}")

    if sample_size > 0 or sample_size is not None:
        preview = lf.head(sample_size)
        if show_columns:
            preview = preview.select([c for c in show_columns if c in preview.columns])
        print(f"Preview ({sample_size} rows):\n{preview}")
    return lf


def build_pipeline(file_path: str, config: PipelineConfig) -> pl.LazyFrame:
    def _inspect(lf: pl.LazyFrame, step: str) -> pl.LazyFrame:
        if config.show_pipeline:
            return inspect_pipe(
                lf, step_name=f"[{config.name}] {step}", sample_size=config.sample_rows
            )
        return lf

    return (
        pl.scan_csv(file_path, try_parse_dates=True)
        .pipe(apply_schema_normalization, config=config)
        .pipe(_inspect, step="Schema Normalized")
        .pipe(apply_scalar_cleaning, config=config)
        .pipe(_inspect, step="Scalars Cleaned")
        .pipe(apply_cat_casting,config = config)
        .pipe(_inspect, step="Category Casted")
        .pipe(apply_str_array_parsing, config=config)
        .pipe(_inspect, step="Arrays Parsed")
        .pipe(apply_regex_extractions, config=config)
        .pipe(_inspect, step="Regex Fields Extracted")
    )

