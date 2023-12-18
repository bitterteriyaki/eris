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

import re
from asyncio import to_thread
from io import BytesIO
from os.path import join
from typing import Any, Dict, Generator, List, Optional, Tuple, cast
from zlib import decompressobj

from discord import Message
from discord.abc import Messageable
from discord.app_commands import describe
from discord.ext.commands import Cog, hybrid_group  # type: ignore

from bot.core import Eris, ErisContext
from bot.utils.fuzzy import finder

RTFM_PAGES = {
    "stable": "https://discordpy.readthedocs.io/en/stable",
    "latest": "https://discordpy.readthedocs.io/en/latest",
    "python": "https://docs.python.org/3",
    "djs": "https://discordjs.dev/docs/packages/discord.js/main",
}

DJS_MANIFEST = "https://docs.discordjs.dev/docs/discord.js/main.json"


class SphinxObjectFileReader:
    __slots__ = ("stream",)

    BUFSIZE = 16 * 1024

    def __init__(self, buffer: bytes) -> None:
        self.stream = BytesIO(buffer)

    def readline(self) -> str:
        return self.stream.readline().decode("utf-8")

    def skipline(self) -> None:
        self.stream.readline()

    def read_compressed_chunks(self) -> Generator[bytes, None, None]:
        decompressor = decompressobj()

        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)

        yield decompressor.flush()

    def read_compressed_lines(self) -> Generator[str, None, None]:
        buf = b""

        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")

            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


class API(Cog):
    """Commands related to Discord's API."""

    __slots__ = ("bot", "_rtfm_cache")

    _rtfm_cache: Dict[str, Dict[str, str]]

    def __init__(self, bot: Eris) -> None:
        self.bot = bot

    def parse_object_inv(
        self, stream: SphinxObjectFileReader, url: str
    ) -> Dict[str, str]:
        result: Dict[str, str] = {}

        inv_version = stream.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        projname = stream.readline().rstrip()[11:]
        stream.readline().rstrip()[11:]

        line = stream.readline()
        if "zlib" not in line:
            raise RuntimeError(
                "Invalid objects.inv file, not z-lib compatible."
            )

        entry_regex = re.compile(
            r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)"
        )

        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())

            if not match:
                continue

            name, directive, _, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")

            if directive == "py:module" and name in result:
                # From the Sphinx repository: due to a bug in 1.1 and
                # below, two inventory entries are created for Python
                # modules, and the first one is correct.
                continue

            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            if projname == "discord.py":
                key = key.replace("discord.ext.commands.", "")
                key = key.replace("discord.", "")

            result[f"{prefix}{key}"] = join(url, location)

        return result

    def parse_objects_json(self, data: Dict[str, Any]) -> Dict[str, str]:
        result: Dict[str, str] = {}
        base_url = RTFM_PAGES["djs"]

        for cls in data["classes"]:
            result[cls["name"]] = f"{base_url}/{cls['name']}"

            try:
                for method in cls["methods"]:
                    if method["name"].startswith("_"):
                        continue

                    name = f"{cls['name']}.{method['name']}"
                    url = f"{base_url}/{cls['name']}#{method['name']}"
                    result[name] = url

                for prop in cls["props"]:
                    if prop["name"].startswith("_"):
                        continue

                    name = f"{cls['name']}.{prop['name']}"
                    url = f"{base_url}/{cls['name']}#{prop['name']}"
                    result[name] = url
            except KeyError:
                pass

        for func in data["functions"]:
            result[func["name"]] = f"{base_url}/{func['name']}"

        return result

    async def build_rtfm_lookup_table(self) -> None:
        cache: Dict[str, Dict[str, str]] = {}

        for key, page in RTFM_PAGES.items():
            cache[key] = {}

            if key == "djs":
                async with self.bot.session.get(DJS_MANIFEST) as resp:
                    if resp.status != 200:
                        raise RuntimeError(
                            "Cannot build RTFM lookup table, try again later."
                        )

                    data = await resp.json()
                    # This function can take a while to run, then we'll
                    # offload it to a thread, so we don't block the
                    # event loop.
                    objects = await to_thread(self.parse_objects_json, data)
                    cache[key] = objects
            else:
                async with self.bot.session.get(page + "/objects.inv") as resp:
                    if resp.status != 200:
                        raise RuntimeError(
                            "Cannot build RTFM lookup table, try again later."
                        )

                    stream = SphinxObjectFileReader(await resp.read())
                    cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(
        self, ctx: ErisContext, key: str, entity: Optional[str] = None
    ) -> Optional[Message]:
        if entity is None:
            return await ctx.reply(
                f"Click [here]({RTFM_PAGES[key]}) to view the documentation."
            )

        if not hasattr(self, "_rtfm_cache"):
            await ctx.typing()
            await self.build_rtfm_lookup_table()

        entity = re.sub(
            r"^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)", r"\1", entity
        )

        if key.startswith("latest"):
            q = entity.lower()

            for name in dir(Messageable):
                if name[0] == "_":
                    continue

                if q == name:
                    entity = f"abc.Messageable.{name}"
                    break

        cache = list(self._rtfm_cache[key].items())
        matches = cast(
            List[Tuple[str, str]],
            finder(entity, cache, key=lambda t: t[0])[:8],
        )

        if len(matches) == 0:
            return await ctx.reply("Could not find anything. Sorry.")

        await ctx.reply("\n".join(f"[`{key}`]({url})" for key, url in matches))

    @hybrid_group(aliases=["rtfd"], fallback="stable")
    @describe(entity="The object to search for.")
    async def rtfm(
        self, ctx: ErisContext, *, entity: Optional[str] = None
    ) -> None:
        """Gives you a documentation link for a discord.py entity."""
        await self.do_rtfm(ctx, "stable", entity)

    @rtfm.command(name="latest", aliases=["dev"])
    @describe(entity="The object to search for.")
    async def rtfm_latest(
        self, ctx: ErisContext, *, entity: Optional[str] = None
    ) -> None:
        """Gives you a documentation link for a discord.py entity."""
        await self.do_rtfm(ctx, "latest", entity)

    @rtfm.command(name="djs")
    @describe(entity="The object to search for.")
    async def rtfm_djs(
        self, ctx: ErisContext, *, entity: Optional[str] = None
    ) -> None:
        """Gives you a documentation link for a discord.js entity."""
        await self.do_rtfm(ctx, "djs", entity)

    @rtfm.command(name="python", aliases=["py"])
    @describe(entity="The object to search for.")
    async def rtfm_python(
        self, ctx: ErisContext, *, entity: Optional[str] = None
    ) -> None:
        """Gives you a documentation link for a Python entity."""
        await self.do_rtfm(ctx, "python", entity)


async def setup(bot: Eris) -> None:
    await bot.add_cog(API(bot))
