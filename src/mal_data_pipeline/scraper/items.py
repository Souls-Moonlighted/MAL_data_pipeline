from dataclasses import dataclass


@dataclass(slots=True)
class AnimeInfoItem:
    """Scrapy item containing metadata for an anime entry.

    Attributes:
        title: Anime title displayed as the primary title.
        url: URL of the anime's MyAnimeList page.
        japanese_title: Anime title written in Japanese.
        english_title: Anime title written in English.
        synonyms: Alternative titles for the anime.
        type: Anime format, such as TV, movie, or OVA.
        episodes: Number of episodes.
        status: Release status, such as currently airing or finished airing.
        aired: Date range during which the anime aired.
        premiered: Season and year of the anime's premiere.
        broadcast: Broadcast schedule information.
        producers: Production companies associated with the anime.
        licensors: Companies that licensed the anime.
        studios: Animation studios that produced the anime.
        source: Source material, such as manga, novel, or original.
        genres: Genres assigned to the anime.
        themes: Themes assigned to the anime.
        duration: Runtime per episode or the total runtime.
        rating: Content rating.
        score: User rating score.
        ranked: Ranking among anime titles.
        popularity: Popularity ranking among anime titles.
        members: Number of MyAnimeList members who have the anime in a list.
        favorites: Number of MyAnimeList members who favorited the anime.
    """

    title: str
    url: str

    japanese_title: str | None = None
    english_title: str | None = None
    synonyms: str | None = None

    type: str | None = None
    episodes: str | None = None
    status: str | None = None

    aired: str | None = None
    premiered: str | None = None
    broadcast: str | None = None

    producers: str | None = None
    licensors: str | None = None
    studios: str | None = None

    source: str | None = None
    genres: str | None = None
    themes: str | None = None

    duration: str | None = None
    rating: str | None = None

    score: str | None = None
    ranked: str | None = None
    popularity: str | None = None
    members: str | None = None
    favorites: str | None = None
