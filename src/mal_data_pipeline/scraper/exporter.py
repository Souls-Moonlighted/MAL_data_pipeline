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
    """Tạo exporter dựa trên phần mở rộng của file đầu ra.

    Args:
        file: File nhị phân đã được mở để ghi dữ liệu.
        output_path: Đường dẫn file đầu ra, dùng để xác định định dạng.

    Returns:
        Exporter tương ứng với định dạng file.

    Raises:
        ValueError: Nếu định dạng file không được hỗ trợ.
    """
    suffix = output_path.suffix.lower()
    exporter_class = EXPORTER_BY_SUFFIX.get(suffix)

    if exporter_class is None:
        supported = ", ".join(sorted(EXPORTER_BY_SUFFIX))
        raise ValueError(
            f"Unsupported export format: {suffix!r}. Supported formats: {supported}"
        )

    return exporter_class(file=file, encoding="utf-8")
