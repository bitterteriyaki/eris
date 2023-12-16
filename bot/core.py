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

from os import environ
from typing import Any, Type, Union

from aiohttp import ClientSession
from discord import Intents, Interaction, Message
from discord.ext.commands import Bot, Context  # type: ignore
from jishaku.modules import find_extensions_in

from bot.utils.context import ErisContext

environ["JISHAKU_NO_UNDERSCORE"] = "true"
environ["JISHAKU_NO_DM_TRACEBACK"] = "true"


class Eris(Bot):
    """Main bot class. The magic happens here."""

    __slots__ = ("session",)

    def __init__(self) -> None:
        self.session = ClientSession()

        super().__init__(command_prefix="?", intents=Intents.all())

    # TODO: Maybe document these methods later?
    async def setup_hook(self) -> None:
        for extension in find_extensions_in("bot/extensions"):
            await self.load_extension(extension)

        await self.load_extension("jishaku")

    async def get_context(
        self,
        origin: Union[Message, Interaction],
        /,
        *,
        cls: Type[Context[Any]] = ErisContext,
    ) -> Any:
        return await super().get_context(origin, cls=cls)

    async def close(self) -> None:
        await self.session.close()
        await super().close()
