import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def example(self, ctx):
        await ctx.send("Это пример команды из ExampleCog!")

def setup(bot):
    bot.add_cog(ExampleCog(bot))