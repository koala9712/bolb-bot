from __future__ import annotations

from typing import TYPE_CHECKING
from os import getenv

from botbase import BotBase
from dotenv import load_dotenv
from nextcord import Intents
from aiosqlite import connect

if TYPE_CHECKING:
    from aiosqlite import Connection

load_dotenv()


intents = Intents.none()
intents.guilds = True
intents.messages = True


class MyBot(BotBase):
    db: Connection

    async def startup(self, *args, **kwargs):
        self.db = await connect("db/bolb.db")

        await self.db.execute(
            """CREATE TABLE IF NOT EXISTS bolb (
                id INTEGER PRIMARY KEY,
                bolbs INTEGER,
                daily INTEGER,
                weekly INTEGER
            )"""
        )
        await self.db.commit()

        await super().startup(*args, **kwargs)


ids = getenv("OWNER_IDS")
assert ids is not None
bot = MyBot(intents=intents, owner_ids=[int(i) for i in ids.strip("[]").split(", ")])


if __name__ == "__main__":
    bot.run(getenv("TOKEN"))
