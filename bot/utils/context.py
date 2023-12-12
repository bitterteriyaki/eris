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

from typing import TYPE_CHECKING, Any, Optional

from discord import Message
from discord.ext import commands

from bot.utils.embed import create_embed

if TYPE_CHECKING:
    from bot.core import Eris
else:
    Eris = Any


class ErisContext(commands.Context[Eris]):
    """Custom context class."""

    async def reply(
        self, content: Optional[str] = None, **kwargs: Any
    ) -> Message:
        """Sends a message to the channel that the command was invoked
        in, but does not ping the author and uses an embed with the
        given content.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message. If this is not given, then the
            message will not have any content. Defaults to ``None``.
        **kwargs: Any
            Any keyword arguments to pass to :meth:`Context.reply`.

        Returns
        -------
        :class:`discord.Message`
            The message that was sent.
        """
        kwargs.setdefault("mention_author", False)
        kwargs.setdefault("embed", create_embed(content, author=self.author))

        return await super().reply(**kwargs)
