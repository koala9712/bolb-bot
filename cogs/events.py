from nextcord.ext import commands
from BotBase import BotBaseBot
from nextcord import Message

class Events(commands.Cog):
    def __init__(self, bot: BotBaseBot):
      self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message_bolb_add_(self, message: Message):
        if message.author.bot:
            return
        if "bolb" not in message.content.lower():
            return
        bolb_users = await self.bot.db.execute("SELECT user_id FROM bolb")
        bolb_users = await bolb_users.fetchall()
        if message.author.id in [i[0] for i in bolb_users]:
            await self.bot.db.execute("UPDATE bolb SET bolbs = bolbs + 1 WHERE user_id = ?", (message.author.id,))
        else:
            await self.bot.db.execute("INSERT INTO bolb (user_id, bolbs, daily_cd, weekly_cd) VALUES(?, ?, ?, ?)", (message.author.id, 1, 0, 0))

        await self.bot.db.commit()

    @commands.Cog.listener("on_command_error")
    async def on_command_error_dm(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, commands.errors.MissingRequiredArgument):
            return await ctx.reply("You are missing a required argument.")
        if isinstance(error, commands.ArgumentParsingError):
            return await ctx.reply("I ran into an error parsing your argument.")

        await ctx.reply(f"I ran into an error, I'll tell the developers to fix it.\n{error}")
        try:
            sham = await self.bot.fetch_user(756258832526868541)
            koala = await self.bot.fetch_user(736147895039819797)
            await sham.send(f"{ctx.author.mention} ran into an error({ctx.message.jump_url}), please fix it.\n{error}")
            await koala.send(f"{ctx.author.mention} ran into an error({ctx.message.jump_url}), please fix it.\n{error}")
        except:
            pass

    @commands.Cog.listener("on_ready")
    async def on_turn_on(self):
        print(f"{self.bot.user} is ready!")

def setup(bot: BotBaseBot):
    bot.add_cog(Events(bot))
