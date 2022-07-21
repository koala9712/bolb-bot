from __future__ import annotations

from asyncio import ensure_future
from typing import TYPE_CHECKING
from traceback import format_exception
from logging import getLogger

from nextcord.ext.commands import (
    Cog,
    CommandNotFound,
    Context,
    MissingRequiredArgument,
    TooManyArguments,
    NotOwner
)
from nextcord.utils import utcnow
from nextcord import Embed, NotFound, Forbidden

if TYPE_CHECKING:
    from nextcord import Message

    from ..__main__ import MyBot

    Context = Context[MyBot]


log = getLogger(__name__)


class Events(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if "bolb" not in message.content.lower():
            return

        await self.bot.db.execute(
            """INSERT INTO bolb
            VALUES (?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE
                SET bolbs = bolb.bolbs + 1""",
            (message.author.id, 1, utcnow(), utcnow()),
        )
        await self.bot.db.commit()

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        error = getattr(error, "original", error)

        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, TooManyArguments):
            await ctx.send("You are giving too many arguments!")
            return
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send("You're missing a required argument.")
        elif isinstance(error, NotOwner):
            return
        else:
            embed = Embed(
                title="Unexpected Error.",
                description=f"```py\n{error}```my dev has been notified",
                color=self.bot.color,
            )
            ensure_future(ctx.send(embed=embed))

            tb = "\n".join(format_exception(type(error), error, error.__traceback__))
            log.error(
                "Command %s raised %s: %s",
                ctx.command,
                type(error).__name__,
                error,
                exc_info=True,
            )

    @Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready!")


def setup(bot: MyBot):
    bot.add_cog(Events(bot))
