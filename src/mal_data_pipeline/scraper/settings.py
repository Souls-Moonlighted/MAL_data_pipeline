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

# Turn off cookies
COOKIES_ENABLED = False

# Turn off cookies
COOKIES_ENABLED = False

# Concurrency
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Download delay
DOWNLOAD_DELAY = 0.25
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 15
AUTOTHROTTLE_TARGET_CONCURRENCY = 3.5

# Retry if rate limit
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]

# Compress site
COMPRESSION_ENABLED = True

# Output
FEED_EXPORT_ENCODING = "utf-8"

# Exporter
EXTENSIONS = {"mal_data_pipeline.scraper.extension.IncrementalExportExtension": 300}
