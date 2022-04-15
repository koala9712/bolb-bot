from nextcord.ext import commands
import config
from typing import Any
import aiosqlite
from nextcord import Activity, ActivityType

class BotBaseBot(commands.Bot):
    def __init__(self):
        self.db: aiosqlite.Connection
        super().__init__("bolb", help_command=None, owner_ids=config.owner_ids, strip_after_prefix=True, activity=Activity(name="99 bottles of bolb on the wall", type=ActivityType.watching))
