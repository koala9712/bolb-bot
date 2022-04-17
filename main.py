import aiosqlite
import config
from BotBase import BotBaseBot
from nextcord.ext import commands


bot = BotBaseBot()
cogs = ["cogs.bolbs", "cogs.events", "jishaku"]

@bot.command(name="help", description="HEEEEEEEELP MEEEEEEE")
async def help_(ctx: commands.Context[commands.Bot]):
    await ctx.reply("nO")


async def startup():
    # cogs
    for extension in cogs:
        try:
            bot.load_extension(extension)
            print(f"Successfully loaded extension {extension}")
        except Exception as e:
            exc = f"{type(e).__name__,}: {e}"
            print(f"Failed to load extension {extension}\n{exc}")
    print("Loaded all cogs...")

    # db
    bot.db = await aiosqlite.connect("bolb.db")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS bolb (user_id INTEGER PRIMARY KEY, bolbs INTEGER, daily_cd INTEGER, weekly_cd INTEGER)")
    await bot.db.commit()

    # bot vars

    bot.owners = [bot.get_user(i) for i in config.owner_ids]

bot.loop.create_task(startup())
bot.run(config.token)
