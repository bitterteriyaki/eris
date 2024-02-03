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

from typing import Optional
from unicodedata import name as get_unicode_name

from discord import Message
from discord.ext.commands import Cog, hybrid_command  # type: ignore

from bot.core import Eris
from bot.utils.context import ErisContext


class Meta(Cog):
    """Commands for utilities related to Discord or the bot itself."""

    __slots__ = ("bot",)

    def __init__(self, bot: Eris) -> None:
        self.bot = bot

    @hybrid_command()
    async def charinfo(
        self, ctx: ErisContext, *, characters: str
    ) -> Optional[Message]:
        """Shows you information about a number of characters."""

        def to_string(character: str) -> str:
            digit = f"{ord(character):x}"

            name = get_unicode_name(character, "Name not found.")
            url = f"https://www.fileformat.info/info/unicode/char/{digit}"

            return f"[`\\U{digit:>08}`]({url}) {name} - {character}"

        content = "\n".join(map(to_string, characters))

        if len(content) > 2000:
            return await ctx.reply("Output too long to display.")

        await ctx.reply(content)


async def setup(bot: Eris) -> None:
    await bot.add_cog(Meta(bot))
