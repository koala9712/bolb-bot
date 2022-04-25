from os import listdir, getenv
from os.path import isfile

from nextcord import Intents
from botbase import BotBase
from dotenv import load_dotenv


load_dotenv()


intents = Intents.none()
intents.guilds = True
intents.messages = True


class MyBot(BotBase):
    ...


bot = MyBot(intents=intents, config_module="bolb-bot.config")


if __name__ == "__main__":
    for filename in listdir("bolb-bot/cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"bolb-bot.cogs.{filename[:-3]}")
        else:
            if isfile(filename):
                print(f"Unable to load {filename[:-3]}")

    bot.loop.create_task(bot.startup())
    bot.run(getenv("TOKEN"))
