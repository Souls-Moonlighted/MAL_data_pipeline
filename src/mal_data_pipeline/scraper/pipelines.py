from typing import Any, ClassVar

from itemadapter import ItemAdapter
from scrapy import Spider


class AnimePipeline:
    """Normalize scraped anime items and convert numeric fields.

    String values are stripped of surrounding whitespace, and empty strings
    are replaced with ``None``. Configured integer and float fields are
    converted when possible; values that cannot be parsed are left unchanged.
    """

    INTEGER_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "episodes",
            "ranked",
            "popularity",
            "members",
            "favorites",
        }
    )

    FLOAT_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "score",
        }
    )

    def process_item(self, item: Any, spider: Spider) -> Any:
        """Normalize an item before passing it to the next pipeline stage.

        Args:
            item: Scraped item to normalize.
            spider: Spider that produced the item.

        Returns:
            The normalized item.
        """
        adapter = ItemAdapter(item)

        self._normalize_strings(adapter)
        self._convert_integers(adapter)
        self._convert_floats(adapter)

        return item

    @staticmethod
    def _normalize_strings(adapter: ItemAdapter) -> None:
        """Strip whitespace from string values in the item adapter.

        Empty strings are replaced with ``None``.

        Args:
            adapter: Adapter whose string values are normalized in place.
        """
        for field_name, value in adapter.items():
            if isinstance(value, str):
                value = value.strip()
                adapter[field_name] = value or None

    def _convert_integers(self, adapter: ItemAdapter) -> None:
        """Convert configured integer fields when their values are parseable.

        Commas and leading number signs are removed before conversion. Values
        that cannot be converted are left unchanged.

        Args:
            adapter: Adapter containing the fields to convert in place.
        """
        for field_name in self.INTEGER_FIELDS:
            value = adapter.get(field_name)

            if value is None:
                continue

            try:
                value = value.replace(",", "").replace("#", "").strip()
                adapter[field_name] = int(value)
            except (ValueError, AttributeError):
                # Keep the original value if it cannot be parsed safely.
                pass

    def _convert_floats(self, adapter: ItemAdapter) -> None:
        """Convert configured float fields when their values are parseable.

        Values that cannot be converted are left unchanged.

        Args:
            adapter: Adapter containing the fields to convert in place.
        """
        for field_name in self.FLOAT_FIELDS:
            value = adapter.get(field_name)

            if value is None:
                continue

            try:
                adapter[field_name] = float(value)
            except (ValueError, TypeError):
                # Keep the original value if it cannot be parsed safely.
                pass
