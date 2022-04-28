from __future__ import annotations

from datetime import datetime, timedelta, timezone
from random import choices, randint
from typing import TYPE_CHECKING

from nextcord import Embed, Member
from nextcord.ext.commands import Cog, Context, command
from nextcord.utils import format_dt, utcnow

if TYPE_CHECKING:
    from ..__main__ import MyBot

    Context = Context[MyBot]


class Bolb(Cog, name="bolb", description="Mess with some bolbs!"):
    def __init__(self, bot: MyBot):
        self.bot = bot

    @command(description="Show your Bolb stats.", aliases=["bolb_amt", "bolbs"])
    async def bolb(self, ctx: Context):
        async with self.bot.db.execute(
            "SELECT bolbs FROM bolb WHERE id=?", (ctx.author.id,)
        ) as c:
            row = await c.fetchone()
            amount = row[0] if row and row[0] else None

        if not amount:
            await ctx.reply("You have no bolbs. Imagine")
        else:
            await ctx.reply(f"You have {amount} bolbs")

    @command(description="Claim your daily bolbs", aliases=["dailyclaim"])
    async def daily(self, ctx: Context):
        async with self.bot.db.execute(
            "SELECT daily FROM bolb WHERE id=?", (ctx.author.id,)
        ) as c:
            row = await c.fetchone()
            daily_raw = row[0] if row and row[0] else 0
            daily = datetime.fromtimestamp(float(daily_raw), tz=timezone.utc)

        next_day = daily + timedelta(days=1)

        if next_day > utcnow():
            return await ctx.reply(
                f"You must wait {format_dt(daily, style='R')}. "
                "You have already claimed your daily"
            )

        await self.bot.db.execute(
            "UPDATE bolb SET bolbs = bolb.bolbs + 7, daily=? WHERE id=?",
            (utcnow().timestamp(), ctx.author.id),
        )
        await self.bot.db.commit()

        await ctx.reply("You claimed your daily bolbs")

    @command(description="Claim your weekly bolbs", aliases=["weeklyclaim"])
    async def weekly(self, ctx: Context):
        async with self.bot.db.execute(
            "SELECT weekly FROM bolb WHERE id=?", (ctx.author.id,)
        ) as c:
            row = await c.fetchone()
            weekly_raw = row[0] if row and row[0] else 0
            weekly = datetime.fromtimestamp(float(weekly_raw), tz=timezone.utc)

        next_week = weekly + timedelta(weeks=1)

        if next_week > utcnow():
            await ctx.reply(
                f"You must wait until {format_dt(weekly, style='R')}. "
                "You have already claimed your weekly."
            )
            return

        await self.bot.db.execute(
            "UPDATE bolb SET bolbs = bolb.bolbs + 45 weekly = ? WHERE id=?",
            (utcnow().timestamp(), ctx.author.id),
        )
        await self.bot.db.commit()

        await ctx.reply("You claimed your weekly bolbs")

    @command(description="Give someone some of your bolbs", aliases=["give"])
    async def pay(self, ctx: Context, user: Member, amount: int):
        async with self.bot.db.execute(
            "SELECT bolbs FROM bolb WHERE id=?", (ctx.author.id,)
        ) as c:
            row = await c.fetchone()
            bolbs_before = row[0] if row and row[0] else 0

        if amount > bolbs_before:
            return await ctx.reply(
                "You don't have that many bolb's to give. Don't try to break me."
            )

        if amount < 1:
            return await ctx.reply("Don't try to break me smh.")

        await self.bot.db.execute(
            "UPDATE bolb SET bolbs = bolb.bolbs - ? WHERE id=?", (amount, ctx.author.id)
        )
        await self.bot.db.execute(
            "UPDATE bolb SET bolbs = bolb.bolbs + ? WHERE id=?", (amount, user.id)
        )
        await self.bot.db.commit()
        await ctx.reply(
            f"You paid {user.mention} `{amount}` bolbs.\n"
            f"You now have `{bolbs_before - amount}` bolbs"
        )

    @command(description="See who has the most bolbs", aliases=["leaderboard"])
    async def lb(self, ctx: Context):
        assert self.bot.user is not None

        users = list(
            await self.bot.db.execute_fetchall(
                "SELECT id, bolbs FROM bolb ORDER BY bolbs LIMIT 10"
            )
        )

        users.reverse()
        user_ids = [row[0] for row in users]

        if ctx.author.id in user_ids:
            user_rank = user_ids.index(ctx.author.id) + 1
            user_bolbs = next(row[1] for row in users if row[0] == ctx.author.id)

            description = (
                f"You have said precisely `{user_bolbs}` bolbs and rank {user_rank}."
            )
        else:
            description = "You have said no bolbs <:angery:903340317770649610>"

        top_10 = [f"` - ` <@{row[0]}> - {row[1]}" for row in users]
        for i in top_10:
            if "397745647723216898" in i:
                i.replace(("- ")[-1], "inf 🐛")

        await ctx.reply(
            embed=Embed(
                description=description,
                colour=self.bot.color,
            )
            .set_author(
                name="Top bolb users",
                url="https://github.com/koala9712/bolb-bot",
                icon_url=self.bot.user.display_avatar.url,
            )
            .add_field(name="Top 10 bolbs", value="\n".join(top_10))
            .set_thumbnail(url=self.bot.user.display_avatar.url)
        )

    @command(description="Gamble your bolbs, win or lose", aliases=["gamble_bolbs"])
    async def gamble(self, ctx: Context, funds: int):
        if funds > 1_000_000_000_000_000:
            return await ctx.reply(
                "Do something useful with your bolbs, stop gambling them."
            )

        if funds < 1:
            return await ctx.reply("Imagine trying to break me smh")

        async with self.bot.db.execute(
            "SELECT bolbs FROM bolb WHERE id=?", (ctx.author.id,)
        ) as c:
            row = await c.fetchone()
            before = row[0] if row else 0

        if funds > before:
            return await ctx.reply(
                "You don't have that many bolb's to gamble. Don't try to break me."
            )

        le_ods = choices((0, 1), (35, 65))  # 65% chance to win, 35% chance to lose.
        odds = le_ods[0]

        if odds == 0:
            pay = randint(funds // 2, funds * 2)
            await ctx.reply(
                f"You won `{pay}` bolbs."
            )  # it's random - the payout of gamble, no less than 50% and more than 200%

            await self.bot.db.execute(
                "UPDATE bolb SET bolbs = bolbs + ? WHERE id=?", (pay, ctx.author.id)
            )
        elif le_ods == 1:
            # you lose your entire bet if you lose
            await ctx.reply(f"You lost `{funds}` bolbs.")
            await self.bot.db.execute(
                "UPDATE bolb SET bolbs = bolbs - ? WHERE id=?", (funds, ctx.author.id)
            )

        await self.bot.db.commit()


def setup(bot: MyBot):
    bot.add_cog(Bolb(bot))
