import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import polars as pl
import tomli_w


@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineConfig:
    """Define the column transformations and runtime options for a pipeline.

    Args:
        name: Human-readable name of the pipeline configuration.
        drop_columns: Column names to remove from the input DataFrame.
        rename_mapping: Mapping from existing column names to their new names.
        scalar_clean_rules: Mapping from column names to cleaning rules. Each
            rule is a tuple of ``(values_to_replace, replacement, dtype)``,
            where ``values_to_replace`` may be a single value or a list of
            values, ``replacement`` is the value to use, and ``dtype`` is the
            optional Polars data type to apply after cleaning.
        cat_cols: ...
        str_array_columns: Column names whose values should be converted to arrays.
        str_array_pattern: Regular expression used to extract array elements from
            string values. The default extracts text enclosed in double quotes.
        regex_extractions: Mapping from output column names to regular
            expressions used to extract values from source data.
        export_config: Whether the configuration should be included in the
            pipeline's exported output.
        enable_inspect: Whether intermediate pipeline data should be inspected.
        sample_rows: Number of rows to use when inspecting intermediate data.

    Notes:
        The configuration is immutable, keyword-only, and uses slots. Mutable
        collection fields receive fresh default values for each instance.
    """

    name: str

    drop_columns: list[str] = field(default_factory=list)

    rename_mapping: dict[str, str] = field(default_factory=dict)

    scalar_clean_rules: dict[
        str, tuple[list[Any] | Any, Any, type[pl.DataType] | None]
    ] = field(default_factory=dict)

    cat_cols: list[str] = field(default_factory=list)

    str_array_columns: list[str] = field(default_factory=list)

    str_array_error_val: list[str] = field(default_factory=list)

    str_array_pattern: str = r'"([^"]+)"'

    regex_extractions: dict[str, str] = field(default_factory=dict)

    show_pipeline: bool = True

    sample_rows: int = 2

    def write_toml(self, path: str | None = None) -> None:
        """Write config to toml file"""
        config_dict = asdict(self)
        if path is None:
            output_path = Path(f"./configs/{self.name}.toml")
        else:
            output_path = Path(path)
        with output_path.open("wb") as f:
            tomli_w.dump(config_dict, f)


def load_pipeline_config(path: str | Path) -> PipelineConfig:
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    return PipelineConfig(**config)
