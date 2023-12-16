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

from logging import getLogger
from typing import cast

from discord import ClientUser
from discord.ext.commands import Cog  # type: ignore
from rich import print
from rich.box import ROUNDED
from rich.table import Table

from bot.core import Eris

log = getLogger(__name__)


class Events(Cog):
    """Handles Discord events."""

    __slots__ = ("bot",)

    def __init__(self, bot: Eris) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        # At this point, :attr:`bot.user` is not ``None`` anymore, so we
        # can safely cast it to :class:`discord.ClientUser` and avoid
        # type errors.
        user = cast(ClientUser, self.bot.user)

        title = ":robot: | Bot Information"
        informations = Table(title=title, box=ROUNDED, title_style="bold")

        informations.add_column("ID", justify="center")
        informations.add_column("Name", justify="center")
        informations.add_column("Discriminator", justify="center")

        informations.add_row(str(user.id), user.name, user.discriminator)

        print(informations)
        log.info(f"Bot is ready. Logged in as '{user}' (ID: {user.id}).")


async def setup(bot: Eris) -> None:
    await bot.add_cog(Events(bot))
