BOT_NAME = "myanimelist"

SPIDER_MODULES = ["mal_data_pipeline.scraper.spiders"]
NEWSPIDER_MODULE = "mal_data_pipeline.scraper.spiders"

# Be polite to the target server.
ROBOTSTXT_OBEY = True

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DOWNLOAD_DELAY = 1.5
CONCURRENT_REQUESTS_PER_DOMAIN = 1

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.5
AUTOTHROTTLE_MAX_DELAY = 10

FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    "mal_data_pipeline.scraper.pipelines.AnimePipeline": 300,
}