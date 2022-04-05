from pydoc import describe
from nextcord.ext.commands import errors
from nextcord.ext import commands
from nextcord import Message
from BotBase import BotBaseBot


import random
import aiosqlite
import config
import time
import random

bot = BotBaseBot("bolb", help_command=None, owner_ids=config.owner_ids)
bot.load_extension("jishaku")

@bot.command(name="help", description="HEEEEEEEELP MEEEEEEE")
async def help_(ctx):
    await ctx.reply("nO")

@bot.command(name="bolb", description="Show your Bolb stats.", aliases=["bolb_amt", "bolbs"])
async def bolb(ctx: commands.Context[commands.Bot]):
    e = await bot.db.execute("SELECT bolb FROM bolb WHERE user_id = ?", (ctx.author.id,))
    e = await e.fetchone()
    if not e:
        await ctx.reply("You have no bolbs. Imagine")
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
    await ctx.reply("You have claimed your daily bolbs")
    return


@bot.command(name="weekly")
async def bolb_weekly(ctx: commands.Context[commands.Bot]):
    weekly_cd_cursor: aiosqlite.Cursor = await bot.db.execute("SELECT weekly_cd FROM bolb WHERE user_id = ?", (ctx.author.id,))
    weekly_cd: int = (await weekly_cd_cursor.fetchone())[0]

    if weekly_cd + 60*60*24*7 > time.time():
        await ctx.reply("You must wait. You have already claimed your weekly.")
        return

    await bot.db.execute("UPDATE bolb SET bolbs = bolbs + 50, daily_cd = ? WHERE user_id = ?", (time.time(), ctx.author.id))
    await bot.db.commit()
    await ctx.reply("You have claimed your weekly bolbs")
    return

@bot.listen("on_message")
async def on_message_bolb_add_(message: Message):
    if "bolb" in message.content:
        await bot.db.execute("UPDATE bolb SET bolbs = bolbs + 1 WHERE user_id = ?", (message.author.id,))

@bot.command("gamble")
async def gamble_them_bolbs(ctx: commands.Context[commands.Bot], gamble_funds):
    gamble_odds = [0, 1]
    bolbs_before = await bot.db.execute("SELECT bolbs FROM bolb WHERE user_id = ?", (ctx.author.id,))
    bolbs_before = await bolbs_before.fetchone()[0]
    if gamble_funds > bolbs_before:
        return await ctx.reply("You don't have that many bolb's to gamble. Don't try to break me.")

    le_ods = random.randchoice(gamble_odds)

    if le_ods == 0:
        le_pay = random.randint(gamble_funds/2, gamble_funds*2)
        await ctx.reply(f"You won `{le_pay}` bolbs.") # it's random - the payout of gamble, no less than 50% and more than 200%
        await bot.db.execute(f"UPDATE bolb SET bolbs = bolbs + {le_pay} WHERE user_id = ?", (ctx.author.id))
    elif le_ods == 1:
        le_pay = random.randint(gamble_funds/2, gamble_funds)
        await ctx.reply(f"You lost `{le_pay}` bolbs.")
        await bot.db.execute(f"UPDATE bolb SET bolbs = bolbs - {le_pay} WHERE user_id = ?", (ctx.author.id))

@bot.listen("on_command_error")
async def on_command_error_dm(ctx, error):
    if isinstance(error, errors.CommandNotFound):
        return
    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    await ctx.reply(f"I ran into an error, I'll tell <@736147895039819797> and <@756258832526868541> to fix it.\n{error}")

async def startup():
    bot.db = aiosqlite.connect("bolb.db")

bot.loop.create_task(startup())
bot.run(config.token)