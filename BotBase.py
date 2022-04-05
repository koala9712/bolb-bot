from typing import Union, Dict, Optional
from nextcord.abc import GuildChannel
from nextcord.ext import commands
from nextcord import Guild, Member, User
from nextcord.ext import commands
from aiosqlite.core import Connection

class BotBaseBot(commands.Bot):
    db: Connection
    async def getch_guild(self, guild_id: int) -> Union[Guild, bool]:
        """Looks up a guild in cache or fetches if not found."""
        guild: Union[Guild, None] = self.get_guild(guild_id)
        if guild:
            return guild

        try:
            guild: Union[Guild, None] = await self.fetch_guild(guild_id)
        except:
            return False
        return guild

    async def getch_user(self, user_id: int) -> Union[User, bool]:
        """Looks up a user in cache or fetches if not found."""
        user: Union[User, None] = self.get_user(user_id)
        if user:
            return user
        try:
            user: Union[User, None] = await self.fetch_user(user_id)
        except:
            return False
        return user

    async def getch_member(self, guild_id: int, member_id: int) -> Union[Member, bool]:
        """Looks up a member in cache or fetches if not found."""

        guild: Union[Guild, None] = await self.fetch_guild(guild_id)
        if not guild:
            return False

        member: Union[Member, None] = guild.get_member(member_id)
        if member is not None:
            return member

        try:
            member: Union[Member, None] = await guild.fetch_member(member_id)
        except:
            return False

        return member

    async def getch_channel(self, channel_id: int) -> Union[GuildChannel, bool]:
        """Looks up a channel in cache or fetches if not found."""
        channel: Union[GuildChannel, None] = self.get_channel(channel_id)
        if channel:
            return channel

        try:
            channel: Union[GuildChannel, None] = await self.fetch_channel(channel_id)
        except:
            return False

        return channel

    async def slash_resync_command(self) -> None:
        cached_guild_data: Dict[Optional[int], dict] = {}
        for app_cmd in self.get_all_application_commands():
            if not app_cmd.command_ids:
                if app_cmd.is_global:
                    if None not in cached_guild_data:
                        cached_guild_data[None] = await self.http.get_global_commands(self.application_id)
                    await self.deploy_application_commands(data=cached_guild_data[None])
                elif app_cmd.is_guild:
                    for guild_id in app_cmd.guild_ids_to_rollout:
                        if guild_id not in cached_guild_data:
                            cached_guild_data[guild_id] = await self.http.get_guild_commands(
                                self.application_id, guild_id
                            )
                        guild = self.get_guild(guild_id)
                        await guild.deploy_application_commands(cached_guild_data[guild_id])
