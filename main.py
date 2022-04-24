from os import listdir, getenv
from os.path import isfile

from nextcord import Intents
from botbase import BotBase


intents = Intents.none()
intents.guilds = True
intents.messages = True


class MyBot(BotBase):
    ...


bot = MyBot(intents=intents)


if __name__ == "__main__":
    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
        else:
            if isfile(filename):
                print(f"Unable to load {filename[:-3]}")

    bot.run(getenv("TOKEN"))
