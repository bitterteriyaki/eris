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

from discord import Embed
from discord.abc import User

EMBED_COLOR = 0x2B2D31


def create_embed(
    content: Optional[str] = None,
    *,
    author: Optional[User] = None,
) -> Embed:
    """Creates an embed with the given content and author, using the
    default embed color.

    Parameters
    ----------
    content: Optional[:class:`str`]
        The content of the embed. If this is not given, then the embed
        will not have any content. Defaults to ``None``.
    author: Optional[:class:`discord.abc.User`]
        The author of the embed. This is used to set the author name
        and icon. If this is not given, then the embed will not have
        an author. Defaults to ``None``.

    Returns
    -------
    :class:`discord.Embed`
        The embed with the given content and author.
    """
    embed = Embed(description=content, color=EMBED_COLOR)

    if author is not None:
        avatar_url = author.display_avatar.url
        embed.set_author(name=author.display_name, icon_url=avatar_url)

    return embed
