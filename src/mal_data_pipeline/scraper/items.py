import scrapy


class AnimeInfoItem(scrapy.Item):
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

    title = scrapy.Field()
    url = scrapy.Field()

    japanese_title = scrapy.Field()
    english_title = scrapy.Field()
    synonyms = scrapy.Field()

    type = scrapy.Field()
    episodes = scrapy.Field()
    status = scrapy.Field()

    aired = scrapy.Field()
    premiered = scrapy.Field()
    broadcast = scrapy.Field()

    producers = scrapy.Field()
    licensors = scrapy.Field()
    studios = scrapy.Field()

    source = scrapy.Field()
    genres = scrapy.Field()
    themes = scrapy.Field()

    duration = scrapy.Field()
    rating = scrapy.Field()

    score = scrapy.Field()
    ranked = scrapy.Field()
    popularity = scrapy.Field()
    members = scrapy.Field()
    favorites = scrapy.Field()