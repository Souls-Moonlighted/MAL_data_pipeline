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

# Concurrency
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 0

# Download delay
DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Output
FEED_EXPORT_ENCODING = "utf-8"

# Exporter
EXTENSIONS = {"mal_data_pipeline.scraper.extension.IncrementalExportExtension": 300}
