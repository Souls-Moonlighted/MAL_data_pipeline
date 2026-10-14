"""Select Scrapy item exporters based on output file extensions."""

from pathlib import Path
from typing import BinaryIO

from scrapy.exporters import (
    BaseItemExporter,
    CsvItemExporter,
    JsonItemExporter,
    JsonLinesItemExporter,
)

EXPORTER_BY_SUFFIX: dict[str, type[BaseItemExporter]] = {
    ".jsonl": JsonLinesItemExporter,
    ".json": JsonItemExporter,
    ".csv": CsvItemExporter,
}


def create_exporter(
    file: BinaryIO,
    output_path: Path,
) -> BaseItemExporter:
    """Create an exporter based on the output file extension.

    Args:
        file: Binary file opened for writing data.
        output_path: Output file path used to determine the format.

    Returns:
        The exporter corresponding to the file format.

    Raises:
        ValueError: If the file format is not supported.
    """
    suffix = output_path.suffix.lower()
    exporter_class = EXPORTER_BY_SUFFIX.get(suffix)

    if exporter_class is None:
        supported = ", ".join(sorted(EXPORTER_BY_SUFFIX))
        raise ValueError(
            f"Unsupported export format: {suffix!r}. Supported formats: {supported}"
        )

    return exporter_class(file=file, encoding="utf-8")
