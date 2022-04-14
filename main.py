import asyncio
import os
import config
import dbman
import aiosqlite
from nextcord import Activity, ActivityType
from BotBase import BotBaseBot

bot = BotBaseBot("bolb", help_command=None, owner_ids=config.owner_ids, strip_after_prefix=True, activity=Activity(name="99 bottles of bolb on the wall", type=ActivityType.watching))
bot.load_extension("jishaku")

for fn in os.listdir("cogs"):
    if fn.endswith(".py"):
        bot.load_extension(f"cogs.{fn[:-3]}")

async def startup():
    bot.db = await aiosqlite.connect("bolb.db")

bot.loop.create_task(startup())
bot.run(config.token)
asyncio.run(dbman.bolb_users())
