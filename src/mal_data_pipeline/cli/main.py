from pathlib import Path
from typing import Annotated, Literal

import typer

from mal_data_pipeline.cli.commands import scraping

app = typer.Typer(help="Command-line interface for MyAnimeList data pipeline.")


app.command(name="spider_list", help="List the available Scrapy spiders.")(
    scraping.show_spider_list
)


@app.command(name="crawl")
def crawl_cli(
    spider: Annotated[str, typer.Argument(help="Name of the spider to run.")],
    resume: Annotated[
        Path | None,
        typer.Option("-r", "--resume", help="Resume directory for the crawl state."),
    ] = None,
    n: Annotated[
        int | None,
        typer.Option("-n", "--count", help="Maximum number of items to scrape."),
    ] = None,
    format: Annotated[
        Literal["csv", "json", "jsonl"],
        typer.Option("-f", "--format", help="Output file format."),
    ] = "csv",
    output: Annotated[
        Path,
        typer.Option("-o", "--output", help="Output file path without an extension."),
    ] = scraping.OUTPUT_DIR,
    log_dir: Annotated[
        Path, typer.Option("--log-dir", help="Path to the crawler log file.")
    ] = scraping.LOG_DIR,
    flush: Annotated[
        bool,
        typer.Option(
            "--flush/--no-flush",
            help="Flush exported items periodically while crawling.",
        ),
    ] = True,
    flush_every: Annotated[
        int,
        typer.Option(
            "--flush-every",
            help="Number of items to scrape before flushing output.",
        ),
    ] = 100,
    cache: Annotated[
        bool,
        typer.Option(
            "--cache/--no-cache", help="Enable cache support for resume mode."
        ),
    ] = True,
    cache_dir: Annotated[
        Path,
        typer.Option("--cache-dir", help="Directory used for crawl cache state."),
    ] = scraping.CACHE_DIR,
):
    """Run a Scrapy spider and save its results using the selected crawl options."""

    scraping.crawl(
        spider=spider,
        resume=resume,
        n=n,
        format=format,
        output=output,
        log_dir=log_dir,
        flush=flush,
        flush_every=flush_every,
        cache=cache,
        cache_dir=cache_dir,
    )


if __name__ == "__main__":
    app()
