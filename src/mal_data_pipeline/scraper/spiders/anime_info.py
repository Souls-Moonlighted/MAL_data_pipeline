from typing import Any, ClassVar

import scrapy
from scrapy.http import Response

from mal_data_pipeline.scraper.items import AnimeInfoItem


class AnimeInfoSpider(scrapy.Spider):
    """Scrape anime details from MyAnimeList's top anime listings.

    The spider follows listing pages and extracts each anime's title and
    sidebar metadata. The optional ``max_items`` argument limits the number of
    anime pages scheduled and scraped.
    """

    name = "MAL_anime_info_spider"
    allowed_domains = ["myanimelist.net"]  # noqa: RUF012

    start_urls = [  # noqa: RUF012
        "https://myanimelist.net/topanime.php",
    ]
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "japanese_title": "Japanese",
        "english_title": "English",
        "synonyms": "Synonyms",
        "type": "Type",
        "episodes": "Episodes",
        "status": "Status",
        "aired": "Aired",
        "premiered": "Premiered",
        "broadcast": "Broadcast",
        "producers": "Producers",
        "licensors": "Licensors",
        "studios": "Studios",
        "source": "Source",
        "genres": "Genres",
        "themes": "Themes",
        "duration": "Duration",
        "rating": "Rating",
        "score": "Score",
        "ranked": "Ranked",
        "popularity": "Popularity",
        "members": "Members",
        "favorites": "Favorites",
    }

    def __init__(
        self,
        max_items: str | int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the spider and configure its optional item limit.

        Args:
            max_items: Maximum number of anime pages to scrape. ``None`` or
                the string ``"none"`` disables the limit.
            *args: Positional arguments passed to the Scrapy spider.
            **kwargs: Keyword arguments passed to the Scrapy spider.

        Raises:
            ValueError: If ``max_items`` is not ``None`` or a positive integer.
        """
        super().__init__(*args, **kwargs)

        if max_items is None or (
            isinstance(max_items, str) and max_items.strip().lower() == "none"
        ):
            self.max_items = None
        else:
            if isinstance(max_items, bool) or not isinstance(max_items, (str, int)):
                raise ValueError("max_items must be None or a positive integer")

            try:
                self.max_items = int(max_items)
            except ValueError as exc:
                raise ValueError(
                    "max_items must be None or a positive integer"
                ) from exc

            if self.max_items < 1:
                raise ValueError("max_items must be None or a positive integer")

        self.scheduled_anime = 0
        self.scraped_items = 0

    def parse(self, response: Response):
        """Schedule anime detail pages and continue through listing pages.

        Args:
            response: Response for a MyAnimeList anime listing page.

        Yields:
            Requests for anime detail pages and, when needed, the next listing
            page.
        """
        anime_links = response.css("tr.ranking-list td.title h3 a::attr(href)").getall()

        remaining = (
            None
            if self.max_items is None
            else max(self.max_items - self.scheduled_anime, 0)
        )

        if not anime_links:
            self.logger.warning("No anime links found on %s", response.url)

        # Schedule only as many anime pages as are still needed.
        links_to_schedule = (
            anime_links if remaining is None else anime_links[:remaining]
        )

        for link in links_to_schedule:
            self.scheduled_anime += 1

            yield response.follow(
                link,
                callback=self.parse_anime,
            )

        # Continue pagination only while the item limit has not been reached.
        if self.max_items is None or self.scheduled_anime < self.max_items:
            next_page = response.css("a.link-blue-box.next::attr(href)").get()

            if next_page:
                yield response.follow(
                    next_page,
                    callback=self.parse,
                )

    def parse_anime(self, response: Response):
        """Extract an anime's title and mapped sidebar metadata.

        Args:
            response: Response for an individual MyAnimeList anime page.

        Yields:
            The populated anime item if a title is found and the item limit has
            not been reached.
        """
        if self.max_items is not None and self.scraped_items >= self.max_items:
            return

        title = response.css("h1.title-name strong::text").get()

        if not title:
            self.logger.warning(
                "Could not find anime title: %s",
                response.url,
            )
            return

        raw_info = self._parse_sidebar(response)

        item = AnimeInfoItem(
            title=title,
            url=response.url,
        )

        for field_name, source_key in self.FIELD_MAP.items():
            item[field_name] = raw_info.get(source_key)

        self.scraped_items += 1
        yield item

    @staticmethod
    def _parse_sidebar(response: Response) -> dict[str, str]:
        """Extract labeled metadata values from an anime page's sidebar.

        Args:
            response: Response for an individual MyAnimeList anime page.

        Returns:
            A dictionary mapping sidebar labels to their extracted text values.
        """
        # Match metadata blocks while excluding label and superscript text.
        blocks = response.xpath(
            "//div["
            "contains("
            'concat(" ", normalize-space(@class), " "), '
            '" spaceit_pad "'
            ")"
            " and .//span["
            "contains("
            'concat(" ", normalize-space(@class), " "), '
            '" dark_text "'
            ")"
            "]"
            "]"
        )

        raw_info = {}

        for block in blocks:
            label = block.css("span.dark_text::text").get()

            if not label:
                continue

            key = label.rstrip(":").strip()

            values = block.xpath(
                ".//text()["
                "not(ancestor::span["
                "contains("
                'concat(" ", normalize-space(@class), " "), '
                '" dark_text "'
                ")"
                "])"
                " and not(ancestor::sup)"
                "]"
            ).getall()

            value = " ".join(" ".join(values).split())

            if value:
                raw_info[key] = value

        return raw_info
