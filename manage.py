"""
Copyright (C) 2023  kyomi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
from contextlib import contextmanager
from logging import INFO, WARN, Formatter, LogRecord, getLogger
from logging.handlers import RotatingFileHandler
from os import environ
from typing import Generator

from click import group
from dotenv import load_dotenv
from rich.logging import RichHandler
from rich.text import Text

from bot.core import Eris


class StreamHandler(RichHandler):
    """A custom logging handler with prettier output."""

    def __init__(self) -> None:
        super().__init__(
            omit_repeated_times=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )

    def get_level_text(self, record: LogRecord) -> Text:
        levelname = record.levelname
        style = f"logging.level.{levelname.lower()}"
        return Text.styled(f"[{levelname}]", style=style)


@contextmanager
def setup_logging() -> Generator[None, None, None]:
    log = getLogger()

    try:
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB

        getLogger("discord").setLevel(INFO)
        getLogger("discord.http").setLevel(WARN)

        log.setLevel(INFO)

        datetime_format = "%Y-%m-%d %H:%M:%S"
        log_format = "[{asctime}] [{levelname}] {name}: {message}"

        handler = RotatingFileHandler(
            filename="logs/eris.log",
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        formatter = Formatter(
            fmt=log_format, datefmt=datetime_format, style="{"
        )

        handler.setFormatter(formatter)

        log.addHandler(handler)
        log.addHandler(StreamHandler())

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]

        for handler in handlers:
            handler.close()
            log.removeHandler(handler)


async def run_bot() -> None:
    load_dotenv("config/.env")

    async with Eris() as bot:
        await bot.start(environ["DISCORD_TOKEN"])


@group()
def main() -> None:
    pass


@main.command()
def runbot() -> None:
    """Run the bot."""
    with setup_logging():
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()
