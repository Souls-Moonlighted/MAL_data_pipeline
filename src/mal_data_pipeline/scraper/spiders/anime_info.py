from collections.abc import Iterator
from typing import Any, ClassVar

import scrapy
from scrapy.http import Request, Response

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

    _VALUE_TEXT_XPATH: ClassVar[str] = (
        ".//text()["
        "not(ancestor::span[contains(@class, 'dark_text')]) "
        "and not(ancestor::sup) "
        "and not(ancestor::span[@itemprop='genre'])"
        "]"
    )

    def __init__(
        self,
        max_items: str | int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the spider and configure its optional item limit."""
        super().__init__(*args, **kwargs)

        if max_items is None or (
            isinstance(max_items, str) and max_items.strip().lower() == "none"
        ):
            self.max_items: int | None = None
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

        self.state: dict[str, int] = getattr(self, "state", {})

    @property
    def scheduled_anime(self) -> int:
        return self.state.get("scheduled_anime", 0)

    @scheduled_anime.setter
    def scheduled_anime(self, value: int) -> None:
        self.state["scheduled_anime"] = value

    @property
    def scraped_items(self) -> int:
        return self.state.get("scraped_items", 0)

    @scraped_items.setter
    def scraped_items(self, value: int) -> None:
        self.state["scraped_items"] = value

    def parse(self, response: Response) -> Iterator[Request]:
        """Schedule anime detail pages and continue through listing pages."""
        anime_links = response.css("tr.ranking-list td.title h3 a::attr(href)").getall()

        if not anime_links:
            self.logger.warning("No anime links found on %s", response.url)
            return

        remaining = (
            None
            if self.max_items is None
            else max(self.max_items - self.scheduled_anime, 0)
        )

        links_to_schedule = (
            anime_links if remaining is None else anime_links[:remaining]
        )

        for link in links_to_schedule:
            self.scheduled_anime += 1
            yield response.follow(
                link,
                callback=self.parse_anime,
                priority=10,
            )

        if (
            self.max_items is None or self.scheduled_anime < self.max_items
        ) and (
            next_page := response.css("a.link-blue-box.next::attr(href)").get()
        ):
            yield response.follow(
                next_page,
                callback=self.parse,
                priority=0,
            )

    def parse_anime(self, response: Response) -> Iterator[AnimeInfoItem]:
        """Extract an anime's title and mapped sidebar metadata."""
        if self.max_items is not None and self.scraped_items >= self.max_items:
            return

        title = (
            response.css("h1.title-name strong::text").get()
            or response.css("h1.title-name::text").get()
        )

        if not title:
            self.logger.warning(
                "Could not find anime title: %s",
                response.url,
            )
            return

        raw_info = self._parse_sidebar(response)

        item = AnimeInfoItem(
            title=title.strip(),
            url=response.url,
            **{
                field_name: raw_info.get(source_key)
                for field_name, source_key in self.FIELD_MAP.items()
            },
        )

        self.scraped_items += 1
        yield item

    @classmethod
    def _parse_sidebar(cls, response: Response) -> dict[str, str]:
        """Extract labeled metadata values from an anime page's sidebar."""
        raw_info: dict[str, str] = {}

        for block in response.css("div.leftside div.spaceit_pad"):
            label = block.css("span.dark_text::text").get()

            if not label:
                continue

            key = label.rstrip(":").strip()
            values = block.xpath(cls._VALUE_TEXT_XPATH).getall()

            if value := " ".join(" ".join(values).split()):
                raw_info[key] = value

        return raw_info