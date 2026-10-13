"""Incremental file export support for Scrapy crawls."""

from pathlib import Path
from typing import Any, BinaryIO

from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.exporters import BaseItemExporter
from scrapy.http import Response

from mal_data_pipeline.scraper.exporter import create_exporter


class IncrementalExportExtension:
    """Export scraped items and flush at configurable intervals."""

    def __init__(
        self,
        output_path: str,
        fields: list[str] | None,
        flush_enabled: bool,
        flush_every: int,
    ) -> None:
        """Initialize the output destination and flush configuration.

        Args:
            output_path: Output file path, including its format extension.
            fields: Optional item fields to export.
            flush_enabled: Whether to flush after each configured batch.
            flush_every: Number of scraped items between flushes.

        Raises:
            ValueError: If ``flush_every`` is less than one.
        """
        if flush_every < 1:
            raise ValueError("flush_every must be at least 1")

        self.output_path: Path = Path(output_path)
        self.fields: list[str] | None = fields
        self.flush_enabled: bool = flush_enabled
        self.flush_every: int = flush_every

        self.file: BinaryIO | None = None
        self.exporter: BaseItemExporter | None = None
        self.items_since_flush: int = 0

    @classmethod
    def from_crawler(
        cls,
        crawler: Crawler,
    ) -> "IncrementalExportExtension":
        """Create the extension and connect its Scrapy signal handlers.

        Raises:
            NotConfigured: If no custom export output path is configured.
        """
        settings = crawler.settings
        output_path = settings.get("EXPORT_OUTPUT_PATH")

        if not output_path:
            raise NotConfigured("Incremental export is not configured")

        fields = settings.getlist("EXPORT_FIELDS") or None

        extension = cls(
            output_path=output_path,
            fields=fields,
            flush_enabled=settings.getbool("EXPORT_FLUSH_ENABLED", True),
            flush_every=settings.getint("EXPORT_FLUSH_EVERY", 10),
        )

        crawler.signals.connect(
            extension.spider_opened,
            signal=signals.spider_opened,
        )
        crawler.signals.connect(
            extension.item_scraped,
            signal=signals.item_scraped,
        )
        crawler.signals.connect(
            extension.spider_closed,
            signal=signals.spider_closed,
        )

        return extension

    def spider_opened(self, spider: Spider) -> None:
        """Open the output file and start the selected item exporter."""
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Start a new output file for this crawl.
        self.file = self.output_path.open("wb")

        self.exporter = create_exporter(
            self.file,
            self.output_path,
        )

        self.exporter.start_exporting()

        # Make initial headers/prefix visible immediately.
        self.file.flush()

    def item_scraped(
        self,
        item: Any,
        response: Response,
        spider: Spider,
    ) -> None:
        """Export a scraped item and flush after the configured batch size.

        Args:
            item: Scrapy item or other item type supported by its exporters.
            response: Response from which the item was scraped.
            spider: Spider that produced the item.
        """
        if self.exporter is None or self.file is None:
            return

        self.exporter.export_item(item)
        self.items_since_flush += 1

        if self.flush_enabled and self.items_since_flush >= self.flush_every:
            self.file.flush()
            self.items_since_flush = 0

    def spider_closed(self) -> None:
        """Finish exporting, flush buffered data, and close the output file."""
        try:
            if self.exporter is not None:
                self.exporter.finish_exporting()

            if self.file is not None:
                self.file.flush()
        finally:
            if self.file is not None:
                self.file.close()
                self.file = None
                self.exporter = None
