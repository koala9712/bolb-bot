from os import getenv, listdir
from os.path import isfile

from botbase import BotBase
from dotenv import load_dotenv
from nextcord import Intents

load_dotenv()


intents = Intents.none()
intents.guilds = True
intents.messages = True


class MyBot(BotBase):
    ...


bot = MyBot(intents=intents, config_module="bolb_bot.config")


if __name__ == "__main__":
    for filename in listdir("bolb_bot/cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"bolb_bot.cogs.{filename[:-3]}")
        else:
            if isfile(filename):
                print(f"Unable to load {filename[:-3]}")

    bot.run(getenv("TOKEN"))
