from nextcord.ext import commands
import config
from typing import Any
import aiosqlite
from nextcord import Activity, ActivityType

class BotBaseBot(commands.Bot):
    def __init__(self):
        self.db: aiosqlite.Connection
        super().__init__("bolb", help_command=None, owner_ids=config.owner_ids, strip_after_prefix=True, activity=Activity(name="99 bottles of bolb on the wall", type=ActivityType.watching))

    async def execute(self, statement: str, args: Any=None):
        await self.db.execute(statement, args if args else ())
        await self.db.commit()
        await self.db.close()

    async def make(self):
        await self.db.execute("CREATE TABLE IF NOT EXISTS bolb (user_id INTEGER PRIMARY KEY, bolbs INTEGER, daily_cd INTEGER, weekly_cd INTEGER)")

    async def put(self):
        await self.db.execute("INSERT INTO bolb (user_id, bolbs, daily_cd, weekly_cd) VALUES (?, ?, ?, ?)", (2, 3, 4, 5))

    async def select(self):
        x = await self.db.execute("SELECT daily_cd from bolb WHERE user_id = ?", (2, ))
        y = await x.fetchone()
        print(y)
        print(type(y))