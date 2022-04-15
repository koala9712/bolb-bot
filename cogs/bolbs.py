import random
import time
import aiosqlite
from nextcord.ext import commands
from nextcord import Member, Embed
from BotBase import BotBaseBot

class Blolb(commands.Cog):
    def __init__(self, bot: BotBaseBot):
      self.bot = bot

    @commands.command(name="bolb", description="Show your Bolb stats.", aliases=["bolb_amt", "bolbs"])
    async def bolb(self, ctx: commands.Context[commands.Bot]):
        e = await self.bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
        e = await e.fetchone()
        if not e:
            await ctx.reply("You have no bolbs. Imagine")
            return
        await ctx.reply(f"You have {e[0]} bolbs")
        return

    @commands.command(name="daily", description="Claim your daily bolbs", aliases=["dailyclaim"])
    async def bolb_daily(self, ctx: commands.Context[commands.Bot]) -> None:
        daily_cd_cursor: aiosqlite.Cursor = await self.bot.db.execute("SELECT daily_cd FROM bolb WHERE user_id = ?", (ctx.author.id, ))
        daily_cd: int = (await daily_cd_cursor.fetchone())[0]

        if daily_cd + 60*60*24 > time.time():
            await ctx.reply("You must wait. You have already claimed your daily")
            return

        await self.bot.db.execute("UPDATE bolb SET bolbs = bolbs + 7, daily_cd = ? WHERE user_id = ?", (time.time(), ctx.author.id))
        await self.bot.db.commit()
        await ctx.reply("You claimed your daily bolbs")
        return

    @commands.command(name="weekly", description="Claim your weekly bolbs", aliases=["weeklyclaim"])
    async def bolb_weekly(self, ctx: commands.Context[commands.Bot]):
        weekly_cd_cursor: aiosqlite.Cursor = await self.bot.db.execute("SELECT weekly_cd FROM bolb WHERE user_id = ?", (ctx.author.id,))
        weekly_cd: int = (await weekly_cd_cursor.fetchone())[0]

        if weekly_cd + 60*60*24*7 > time.time():
            await ctx.reply("You must wait. You have already claimed your weekly.")
            return

        await self.bot.db.execute("UPDATE bolb SET bolbs = bolbs + 45, weekly_cd = ? WHERE user_id = ?", (time.time(), ctx.author.id))
        await self.bot.db.commit()
        await ctx.reply("You claimed your weekly bolbs")
        return

    @commands.command(name="pay", description="Give someone some of your bolbs", aliases=["give"])
    async def pay_bolbs(self, ctx: commands.Context[commands.Bot], user: Member=None, amount:int=None):
        if not user or not amount:
            return await ctx.reply("You use it like this: `bolb pay <user> <amount>`")

        bolbs_before = await self.bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
        bolbs_before = (await bolbs_before.fetchone())[0]

        if amount > bolbs_before:
            return await ctx.reply("You don't have that many bolb's to give. Don't try to break me.")

        await self.bot.db.execute(f"UPDATE bolb SET bolbs = bolbs - {amount} WHERE user_id = ?", (ctx.author.id, ))
        await self.bot.db.execute(f"UPDATE bolb SET bolbs = bolbs + {amount} WHERE user_id = ?", (user.id, ))
        await ctx.reply(f"You paid {user.mention} `{amount}` bolbs.\nYou now have {bolbs_before-amount} bolbs")

    @commands.command(name="lb", description="See who has the most bolbs", aliases=["leaderboard"])
    async def bolb_lb(self, ctx: commands.Context[commands.Bot]):
        bolb_users = await self.bot.db.execute("SELECT user_id, bolbs FROM bolb ORDER BY bolbs")
        bolb_users = await bolb_users.fetchall()
        bolb_users.reverse()
        top_10_user_ids = [i[0] for i in bolb_users[:10]]

        if ctx.author.id in top_10_user_ids:
            user_rank = top_10_user_ids.index(ctx.author.id) + 1
            user_bolbs = [i[1] for i in bolb_users if i[0] == ctx.author.id][0]
            description = f"You have said precisely `{user_bolbs}` bolbs and rank {user_rank}."
        else:
            description = "You have said no bolbs <:angery:903340317770649610>"

        top_10 = [f"` - ` <@{i[0]}> - {i[1]}" for i in bolb_users[:10]]

        await ctx.reply(content="<:bolbbolb:925746516101066753>",
            embed=Embed(description=description)
            .set_author(name="Top bolb users", url="https://github.com/koala9712/bolb-bot", icon_url=self.bot.user.display_avatar.url)
            .add_field(name="Top 10 bolbs", value="\n".join(top_10))
            .set_thumbnail(url=self.bot.user.display_avatar.url)
    )

    @commands.command(name="gamble", description="Gamble your bolbs, win or lose", aliases=["gamble_bolbs"])
    async def gamble_them_bolbs(self, ctx: commands.Context[commands.Bot], gamble_funds: int):


        bolbs_before = await self.bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
        bolbs_before = (await bolbs_before.fetchone())[0]
        if gamble_funds > bolbs_before:
            return await ctx.reply("You don't have that many bolb's to gamble. Don't try to break me.")

        le_ods = random.choices((0, 1), (35, 65)) # 65% chance to win, 35% chance to lose.
        le_ods = le_ods[0]

        if le_ods == 0:
            le_pay = random.randint(gamble_funds if gamble_funds % 2 == 0 else gamble_funds-1/2, gamble_funds*2)
            await ctx.reply(f"You won `{le_pay}` bolbs.") # it's random - the payout of gamble, no less than 50% and more than 200%
            await self.bot.db.execute(f"UPDATE bolb SET bolbs = bolbs + {le_pay} WHERE user_id = ?", (ctx.author.id, ))
            await self.bot.db.commit()
        elif le_ods == 1:
            # you lose your entire bet if you lose
            await ctx.reply(f"You lost `{gamble_funds}` bolbs.")
            await self.bot.db.execute(f"UPDATE bolb SET bolbs = bolbs - {gamble_funds} WHERE user_id = ?", (ctx.author.id, ))
            await self.bot.db.commit()

def setup(bot: BotBaseBot):
    bot.add_cog(Blolb(bot))
