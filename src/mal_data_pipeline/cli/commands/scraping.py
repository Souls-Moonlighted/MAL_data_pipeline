import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal

import tzlocal

ROOT = Path(__file__).resolve().parents[4]

CURRENT_DATETIME = datetime.now(tzlocal.get_localzone()).strftime("%m-%d-%y_%H_%M")

OUTPUT_DIR = ROOT / "data" / "raw" / f"[{CURRENT_DATETIME}]_anime_info"
LOG_DIR = ROOT / "logs" / "scraper" / f"[{CURRENT_DATETIME}]_crawl.log"


def show_spider_list() -> None:
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
    format: Literal["csv", "json", "jsonl", "xml"] = "csv",
    output: Path = OUTPUT_DIR,
    log_dir: Path = LOG_DIR,
    order: bool = True,
):

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
    ]

    if n is not None:
        command.extend(["-a", f"max_items={n}"])
    if order:
        command.extend(["-s", "SCHEDULER_MEMORY_QUEUE=scrapy.squeues.FifoMemoryQueue"])
    try:
        subprocess.run(command, text=True, check=True)
    except subprocess.CalledProcessError as err:
        print(f"Runtime error (Exit code {err.returncode}):\n{err.stderr}")
