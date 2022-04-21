from nextcord.ext import commands
from BotBase import BotBaseBot
from nextcord import Message
from nextcord.ext.commands import errors
import nextcord
import traceback


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
    async def on_command_error_dm(self, ctx, error):
        if isinstance(error, errors.CommandNotFound):
            return
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        elif isinstance(error, errors.TooManyArguments):
            await ctx.send("You are giving too many arguments!")
            return
        elif isinstance(error, errors.BadArgument):
            await ctx.send(
                "The library ran into an error attempting to parse your argument."
            )
            return
        elif isinstance(error, errors.MissingRequiredArgument):
            await ctx.send("You're missing a required argument.")

        elif isinstance(error, nextcord.NotFound) and "Unknown interaction" in str(error):
            return

        else:
            await ctx.send(
                f"This command raised an exception: `{type(error)}:{str(error)}`"
            )

        deliminator = "\n"
        message = f"{type(error).__name__}: {ctx.message.jump_url} while using command {ctx.invoked_with}\n```py\n{deliminator.join(traceback.format_exception(type(error), error, error.__traceback__))}```"
        for user_id in self.bot.owner_ids:
            user = self.bot.get_user(user_id)
            await user.send(message)

    @commands.Cog.listener("on_ready")
    async def on_turn_on(self):
        print(f"{self.bot.user} is ready!")

def setup(bot: BotBaseBot):
    bot.add_cog(Events(bot))
