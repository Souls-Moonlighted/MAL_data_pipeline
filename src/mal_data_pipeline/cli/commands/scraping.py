"""Helpers for invoking Scrapy commands from the project CLI."""

import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

import tzlocal

ROOT: Path = Path(__file__).resolve().parents[4]

CURRENT_DATETIME: str = datetime.now(tzlocal.get_localzone()).strftime("%m-%d-%y_%H_%M")

OUTPUT_DIR: Path = ROOT / "data" / "raw" / f"[{CURRENT_DATETIME}]_anime_info"
LOG_DIR: Path = ROOT / "logs" / "scraper" / f"[{CURRENT_DATETIME}]_crawl.log"


def show_spider_list() -> None:
    """Print the spiders registered with the configured Scrapy project."""
    command = "scrapy list"
    try:
        run = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        print(run.stdout)
    except subprocess.CalledProcessError as err:
        print(f"Runtime error (Exit code {err.returncode}):\n{err.stderr}")
    except subprocess.TimeoutExpired:
        print("Timeout error !")


def crawl(
    spider: str,
    n: int | None = None,
    format: Literal["csv", "json", "jsonl"] = "csv",
    output: Path = OUTPUT_DIR,
    log_dir: Path = LOG_DIR,
    flush: bool = True,
    flush_every: int = 10,
) -> None:
    """Run a spider and write its scraped items to the selected output.

    Args:
        spider: Name of the Scrapy spider to run.
        n: Optional maximum number of items to scrape.
        format: Output format, either CSV, JSON, or JSON Lines.
        output: Output path without the format extension.
        log_dir: Path where Scrapy writes its log.
        flush: Whether to flush the output periodically while crawling.
        flush_every: Number of scraped items between flushes.

    Raises:
        SystemExit: If the Scrapy process exits with a non-zero status.
    """

    output.parent.mkdir(parents=True, exist_ok=True)
    log_dir.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "scrapy",
        "crawl",
        spider,
        "-O",
        f"{output}.{format}",
        "--logfile",
        str(log_dir),
        "--loglevel",
        "INFO",
    ]

    if n is not None:
        command.extend(["-a", f"max_items={n}"])
    if flush:
        command.remove("-O")
        command.remove(f"{output}.{format}")
        command.extend(
            [
                "-s",
                f"EXPORT_OUTPUT_PATH={output}.{format}",
                "-s",
                "EXPORT_FLUSH_ENABLED=True",
                "-s",
                f"EXPORT_FLUSH_EVERY={flush_every}",
            ]
        )
    try:
        subprocess.run(command, text=True, check=True)
    except subprocess.CalledProcessError as err:
        print(
            f"Runtime error (Exit code {err.returncode}). See log: {log_dir}",
            file=sys.stderr,
        )
        raise SystemExit(err.returncode) from None
