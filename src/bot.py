import discord
from discord.ext import commands
import os
from utils.database import Database
from config import Config
from tree_cls import CustomCommandTree
import logging

Config().start()
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG if Config().DEBUG else logging.INFO)
intents = discord.Intents.all()
intents.members = True  # Включаем intent для отслеживания участников
bot = commands.Bot(
    command_prefix=Config.PREFIX, intents=intents, tree_cls=CustomCommandTree
)

# Инициализация базы данных
db = Database()


@bot.event
async def on_ready():
    db.create_tables()


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandInvokeError):
        message = f"Произошла ошибка"
        if Config.DEBUG:
            message += f"\n```{error}```"
        await ctx.reply(message, ephemeral=True)


@bot.command()
async def ping(ctx: commands.Context):
    await ctx.message.add_reaction("✅")


@bot.command()
async def update_config(ctx: commands.Context):
    await ctx.message.add_reaction("✅")
@bot.command()
async def wait_me(ctx: commands.Context):
    await ctx.message.add_reaction("✅")


@bot.command()
# @commands.has_permissions(manage_messages=True)  # Только для администраторов
async def debug(ctx: commands.Context, level: bool):
    """
    Изменить уровень отладки
    Использование: !debug True/False
    """
    try:
        Config().update_debug_level(level)
        await ctx.message.add_reaction("✅")
        await ctx.send(f"Уровень отладки изменен на: {'DEBUG' if level else 'INFO'}")
    except Exception as e:
        await ctx.send(f"Ошибка при изменении уровня отладки: {str(e)}")


if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
