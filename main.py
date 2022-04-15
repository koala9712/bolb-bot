import os
import aiosqlite
import config
from BotBase import BotBaseBot

bot = BotBaseBot()
bot.load_extension("jishaku")

for fn in os.listdir("cogs"):
    if fn.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{fn[:-3]}")
            print(f"{fn} Cog loaded!")
        except Exception as err:
            print(f"There was an error with {fn}: {err}")

async def startup():
    bot.db = await aiosqlite.connect("bolb.db")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS bolb (user_id INTEGER PRIMARY KEY, bolbs INTEGER, daily_cd INTEGER, weekly_cd INTEGER)")
    await bot.db.commit()

bot.loop.create_task(startup())
bot.run(config.token)