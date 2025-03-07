import logging
import loggers
import discord
from discord.ext import commands
import os
from utils.database import Database
from config import Config
from tree_cls import CustomCommandTree
from globals import WaitingAnswer, yes, no
from utils.menu_state import MenuManager, MenuState

config = Config()
menu_manager = MenuManager()

waiting = WaitingAnswer()
logger = logging.getLogger("discord")
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
async def start_menu(ctx: commands.Context):
    """Начать заполнение анкеты"""
    menu_manager.start_menu(ctx.author.id)
    await ctx.send("Пожалуйста, введите ваше имя:")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    user_id = message.author.id
    current_state = menu_manager.get_current_state(user_id)

    if current_state:
        response = menu_manager.process_answer(user_id, message.content)
        if response:
            await message.channel.send(response)
        elif current_state == MenuState.WAITING_PHOTO:
            if message.attachments:
                menu_manager.user_data[user_id]["photo"] = message.attachments[0].url
            summary_embed = menu_manager.get_summary_embed(user_id)
            await message.channel.send(embed=summary_embed)
    else:
        await bot.process_commands(message)


@bot.command()
async def ping(ctx: commands.Context):
    await ctx.message.add_reaction(yes)


@bot.command()
async def update_config(ctx: commands.Context):
    await ctx.message.add_reaction(yes)


@bot.command()
async def wait_me(ctx: commands.Context):
    await ctx.message.add_reaction(yes)
    if ctx.author.id not in waiting:
        waiting.add_user(ctx.author.id)
    else:
        waiting.remove_user(ctx.author.id)


# @commands.has_permissions(manage_messages=True)  # Только для администраторов
@bot.command()
async def debug(ctx: commands.Context, level: bool):
    """
    Изменить уровень отладки
    Использование: !debug True/False
    """
    try:
        Config().update_debug_level(level)
        await ctx.message.add_reaction(yes)
        await ctx.send(
            f"Уровень отладки изменен на: {'DEBUG' if level else 'INFO'}",
            ephemeral=True,
        )
    except Exception as e:
        await ctx.send(f"Ошибка при изменении уровня отладки: {str(e)}")


if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
