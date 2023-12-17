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

from typing import Any, List, Mapping, Optional

from discord.ext.commands import (  # type: ignore
    Cog,
    Command,
    Group,
    HelpCommand,
)

from bot.core import Eris
from bot.utils.embed import create_embed

BOOKMARK_TABS_EMOJI = "\U0001f4d1"
SILHOUETTE_EMOJI = "\U0001f465"
PIN_EMOJI = "\U0001f4cc"


class Help(HelpCommand):
    """A custom help command."""

    __slots__ = ()

    def __init__(self, **options: Any) -> None:
        super().__init__(**options)
        self.command_attrs["help"] = "Shows this message."

    async def send_error_message(self, error: str) -> None:
        ctx = self.context
        embed = create_embed(error, author=ctx.author)

        await ctx.reply(embed=embed)

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]]
    ) -> None:
        ctx = self.context
        cmd = self.get_command_signature(self._command_impl)

        content = f"Use `{cmd}` to get help on a command."
        embed = create_embed(content, author=ctx.author)

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)

            if cog is None or not filtered:
                continue

            name = cog.qualified_name
            commands = [f"`{command.name}`" for command in filtered]

            embed.add_field(name=name, value=", ".join(commands), inline=False)

        await ctx.reply(embed=embed)

    async def send_cog_help(self, cog: Cog) -> None:
        ctx = self.context
        embed = create_embed(cog.description, author=ctx.author)

        cmd = self.get_command_signature(self._command_impl)
        embed.title = f"{BOOKMARK_TABS_EMOJI} `{cmd}`"

        filtered = await self.filter_commands(cog.get_commands(), sort=True)

        if filtered:
            commands = [f"`{command.name}`" for command in filtered]
            embed.add_field(
                name="\U0001f4cc Commands",
                value=", ".join(commands),
                inline=False,
            )

        await ctx.reply(embed=embed)

    async def send_group_help(self, group: Group[Any, ..., Any]) -> None:
        ctx = self.context
        embed = create_embed(group.help, author=ctx.author)

        cmd = self.get_command_signature(group)
        embed.title = f"{BOOKMARK_TABS_EMOJI} `{cmd}`"

        if group.aliases:
            name = f"{SILHOUETTE_EMOJI} Aliases"
            aliases = ", ".join(f"`{alias}`" for alias in group.aliases)

            embed.add_field(name=name, value=aliases, inline=False)

        if group.commands:
            name = "\U0001f4cc Subcommands"
            commands = ", ".join(
                f"`{command.name}`" for command in group.commands
            )

            embed.add_field(name=name, value=commands, inline=False)

        await ctx.reply(embed=embed)

    async def send_command_help(self, command: Command[Any, ..., Any]) -> None:
        ctx = self.context
        embed = create_embed(command.help, author=ctx.author)

        cmd = self.get_command_signature(command)
        embed.title = f"{BOOKMARK_TABS_EMOJI} `{cmd}`"

        if command.aliases:
            name = f"{PIN_EMOJI} Aliases"
            aliases = ", ".join(f"`{alias}`" for alias in command.aliases)

            embed.add_field(name=name, value=aliases, inline=False)

        await ctx.reply(embed=embed)


class Support(Cog):
    """Commands related to user support."""

    __slots__ = ("bot", "original_help_command")

    def __init__(self, bot: Eris) -> None:
        self.bot = bot
        self.original_help_command = bot.help_command

        bot.help_command = Help()
        bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self.original_help_command


async def setup(bot: Eris) -> None:
    await bot.add_cog(Support(bot))
