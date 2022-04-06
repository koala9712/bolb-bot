import re
import nextcord
from nextcord.ext.commands import errors
from nextcord.ext import commands
from nextcord import Message
from BotBase import BotBaseBot


import random
import aiosqlite
import config
import time
import random

bot = BotBaseBot("bolb", help_command=None, owner_ids=config.owner_ids, strip_after_prefix=True)
bot.load_extension("jishaku")

@bot.command(name="help", description="HEEEEEEEELP MEEEEEEE")
async def help_(ctx):
    await ctx.reply("nO")

@bot.command(name="bolb", description="Show your Bolb stats.", aliases=["bolb_amt", "bolbs"])
async def bolb(ctx: commands.Context[commands.Bot]):
    e = await bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
    e = await e.fetchone()
    if not e:
        await ctx.reply("You have no bolbs. Imagine")
        return
    await ctx.reply(f"You have {e[0]} bolbs")
    return


@bot.command(name="daily")
async def bolb_daily(ctx: commands.Context[commands.Bot]) -> None:
    daily_cd_cursor: aiosqlite.Cursor = await bot.db.execute("SELECT daily_cd FROM bolb WHERE user_id = ?", (ctx.author.id, ))
    daily_cd: int = (await daily_cd_cursor.fetchone())[0]

    if daily_cd + 60*60*24 > time.time():
        await ctx.reply("You must wait. You have already claimed your daily")
        return

    await bot.db.execute("UPDATE bolb SET bolbs = bolbs + 7, daily_cd = ? WHERE user_id = ?", (time.time(), ctx.author.id))
    await bot.db.commit()
    await ctx.reply("You claimed your daily bolbs")
    return


@bot.command(name="weekly")
async def bolb_weekly(ctx: commands.Context[commands.Bot]):
    weekly_cd_cursor: aiosqlite.Cursor = await bot.db.execute("SELECT weekly_cd FROM bolb WHERE user_id = ?", (ctx.author.id,))
    weekly_cd: int = (await weekly_cd_cursor.fetchone())[0]

    if weekly_cd + 60*60*24*7 > time.time():
        await ctx.reply("You must wait. You have already claimed your weekly.")
        return

    await bot.db.execute("UPDATE bolb SET bolbs = bolbs + 45, weekly_cd = ? WHERE user_id = ?", (time.time(), ctx.author.id))
    await bot.db.commit()
    await ctx.reply("You claimed your weekly bolbs")
    return

@bot.listen("on_message")
async def on_message_bolb_add_(message: Message):
    if message.author.bot:
        return
    if "bolb" not in message.content.lower():
        return
    bolb_users = await bot.db.execute("SELECT user_id FROM bolb")
    bolb_users = await bolb_users.fetchall()
    if message.author.id in [i[0] for i in bolb_users]:
        await bot.db.execute("UPDATE bolb SET bolbs = bolbs + 1 WHERE user_id = ?", (message.author.id,))
    else:
        await bot.db.execute("INSERT INTO bolb (user_id, bolbs, daily_cd, weekly_cd) VALUES(?, ?, ?, ?)", (message.author.id, 1, 0, 0))

    await bot.db.commit()

@bot.command("gamble")
async def gamble_them_bolbs(ctx: commands.Context[commands.Bot], gamble_funds: int):
    if gamble_funds < 1:
        return await ctx.reply("You must gamble at least 1 bolb.")

    gamble_funds = gamble_funds if gamble_funds % 2 == 0 else gamble_funds + 1
    bolbs_before = await bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
    bolbs_before = (await bolbs_before.fetchone())[0]
    if gamble_funds > bolbs_before:
        return await ctx.reply("You don't have that many bolb's to gamble. Don't try to break me.")

    le_ods = random.choices((0, 1), (65, 35)) # 65% chance to win, 35% chance to lose.
    le_ods = le_ods[0]

    if le_ods == 0:
        le_pay = random.randint(gamble_funds/2, gamble_funds*2)
        await ctx.reply(f"You won `{le_pay}` bolbs.") # it's random - the payout of gamble, no less than 50% and more than 200%
        await bot.db.execute(f"UPDATE bolb SET bolbs = bolbs + {le_pay} WHERE user_id = ?", (ctx.author.id, ))
        await bot.db.commit()
    elif le_ods == 1:
        # you lose your entire bet if you lose
        await ctx.reply(f"You lost `{gamble_funds}` bolbs.")
        await bot.db.execute(f"UPDATE bolb SET bolbs = bolbs - {gamble_funds} WHERE user_id = ?", (ctx.author.id, ))
        await bot.db.commit()

@bot.command("lb", aliases=["leaderboard"])
async def bolb_lb(ctx: commands.Context):
    bolb_users = await bot.db.execute("SELECT user_id, bolbs FROM bolb ORDER BY bolbs")
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
        embed=nextcord.Embed(description=description)
        .set_author(name="Top bolb users", url="https://github.com/koala9712/bolb-bot", icon_url=bot.user.display_avatar.url)
        .add_field(name="Top 10 bolbs", value="\n".join(top_10))
        .set_thumbnail(url=bot.user.display_avatar.url)
    )

@bot.command("pay", aliases=["give"])
async def pay_bolbs(ctx, user: nextcord.Member=None, amount:int=None):
    if not user or not amount:
        return await ctx.reply("You use it like this: `bolb pay <user> <amount>`")

    bolbs_before = await bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
    bolbs_before = (await bolbs_before.fetchone())[0]

    if amount > bolbs_before:
        return await ctx.reply("You don't have that many bolb's to give. Don't try to break me.")

    await bot.db.execute(f"UPDATE bolb SET bolbs = bolbs - {amount} WHERE user_id = ?", (ctx.author.id, ))
    await bot.db.execute(f"UPDATE bolb SET bolbs = bolbs + {amount} WHERE user_id = ?", (user.id, ))
    await ctx.reply(f"You paid {user.mention} `{amount}` bolbs.\nYou now have {bolbs_before-amount} bolbs")


@bot.listen("on_command_error")
async def on_command_error_dm(ctx, error):
    if isinstance(error, errors.CommandNotFound):
        return
    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    if isinstance(error, errors.MissingRequiredArgument):
        return await ctx.reply("You are missing a required argument.")
    if isinstance(error, commands.ArgumentParsingError):
        return await ctx.reply("I ran into an error parsing your argument.")
    await ctx.reply(f"I ran into an error, I'll tell <@736147895039819797> and <@756258832526868541> to fix it.\n{error}")

async def startup():
    bot.db = await aiosqlite.connect("bolb.db")

bot.loop.create_task(startup())
bot.run(config.token)