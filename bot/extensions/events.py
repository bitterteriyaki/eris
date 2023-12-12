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

from discord.ext.commands import Cog # type: ignore

from bot.core import Eris


class Events(Cog):
    """Handles Discord events."""

    __slots__ = ("bot",)

    def __init__(self, bot: Eris) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f"Logged in as {self.bot.user}.")


async def setup(bot: Eris) -> None:
    await bot.add_cog(Events(bot))
